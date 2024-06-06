#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <sys/event.h>
#include <sys/socket.h>
#include <errno.h>
#include <cdb.h>
#include "plugins/plugin.h"

#define PORT 8080
#define BUFFER_SIZE 8192
#define MAX_EVENTS 1024
#define MAX_CLIENTS 10000

char *find_redirect(const char *key) {
    struct cdb cdb;
    int fd = open("redirects.cdb", O_RDONLY);
    if (fd < 0) {
        perror("open");
        return NULL;
    }

    cdb_init(&cdb, fd)

    unsigned klen = strlen(key);
    char *value = NULL;
    unsigned vlen;
    char *result = NULL;

    if (cdb_find(&cdb, key, klen) > 0) {
        vlen = cdb_datalen(&cdb);
        value = malloc(vlen + 1);
        if (!value) {
            perror("malloc");
            cdb_free(&cdb);
            close(fd);
            return NULL;
        }
        cdb_read(&cdb, value, vlen, cdb_datapos(&cdb));
        value[vlen] = '\0';
        result = strdup(value);
        free(value);
    }

    cdb_free(&cdb);
    close(fd);
    return result;
}

void handle_request(int client_socket, const char *method, const char *path, const char *auth_header) {
    RequestData request_data = {method, path, auth_header, client_socket, NULL};

    execute_plugins(PRE_ROUTING, &request_data);

    char *redirect_url = find_redirect(path + 1);
    if (redirect_url) {
        char response[BUFFER_SIZE];
        snprintf(response, sizeof(response), "HTTP/1.1 302 Found\nLocation: %s\nContent-Length: 0\n\n", redirect_url);
        send(client_socket, response, strlen(response), 0);
        free(redirect_url);
    } else {
        const char *response = "HTTP/1.1 404 Not Found\nContent-Type: text/plain\nContent-Length: 9\n\nNot Found";
        send(client_socket, response, strlen(response), 0);
    }

    execute_plugins(POST_ROUTING, &request_data);
    close(client_socket);
}

int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

void cleanup(int server_fd, int kq) {
    if (server_fd >= 0) close(server_fd);
    if (kq >= 0) close(kq);
}

int main() {
    int server_fd = -1, new_socket, kq = -1, nev;
    struct sockaddr_in address;
    struct kevent change_event, event[MAX_EVENTS];
    socklen_t addrlen;
    char buffer[BUFFER_SIZE];

    // Crear el socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        cleanup(server_fd, kq);
        exit(EXIT_FAILURE);
    }

    // Configurar la dirección y puerto del servidor
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Adjuntar el socket a la dirección y puerto
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        cleanup(server_fd, kq);
        exit(EXIT_FAILURE);
    }

    // Escuchar en el socket
    if (listen(server_fd, 1000) < 0) {
        perror("listen");
        cleanup(server_fd, kq);
        exit(EXIT_FAILURE);
    }

    // Configurar el socket del servidor como no bloqueante
    if (set_nonblocking(server_fd) == -1) {
        perror("fcntl");
        cleanup(server_fd, kq);
        exit(EXIT_FAILURE);
    }

    // Crear el kqueue
    if ((kq = kqueue()) == -1) {
        perror("kqueue");
        cleanup(server_fd, kq);
        exit(EXIT_FAILURE);
    }

    // Inicializar el evento para el socket maestro
    EV_SET(&change_event, server_fd, EVFILT_READ, EV_ADD | EV_ENABLE, 0, 0, NULL);
    if (kevent(kq, &change_event, 1, NULL, 0, NULL) == -1) {
        perror("kevent");
        cleanup(server_fd, kq);
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d\n", PORT);

    while (1) {
        nev = kevent(kq, NULL, 0, event, MAX_EVENTS, NULL);
        if (nev < 0) {
            perror("kevent error");
            cleanup(server_fd, kq);
            exit(EXIT_FAILURE);
        }

        for (int i = 0; i < nev; i++) {
            if (event[i].flags & EV_ERROR) {
                fprintf(stderr, "EV_ERROR: %s\n", strerror(event[i].data));
                cleanup(server_fd, kq);
                exit(EXIT_FAILURE);
            }

            if (event[i].ident == server_fd) {
                addrlen = sizeof(address);
                if ((new_socket = accept(server_fd, (struct sockaddr *)&address, &addrlen)) < 0) {
                    if (errno != EWOULDBLOCK && errno != EAGAIN) {
                        perror("accept");
                    }
                    continue;
                }

                printf("New connection, socket fd is %d, ip is : %s, port: %d\n",
                       new_socket, inet_ntoa(address.sin_addr), ntohs(address.sin_port));

                if (set_nonblocking(new_socket) == -1) {
                    perror("fcntl");
                    close(new_socket);
                    continue;
                }

                EV_SET(&change_event, new_socket, EVFILT_READ, EV_ADD | EV_ENABLE, 0, 0, NULL);
                if (kevent(kq, &change_event, 1, NULL, 0, NULL) == -1) {
                    perror("kevent");
                    close(new_socket);
                }
            } else {
                int sd = event[i].ident;
                int valread = read(sd, buffer, BUFFER_SIZE);
                if (valread == 0) {
                    getpeername(sd, (struct sockaddr *)&address, &addrlen);
                    printf("Host disconnected, ip %s, port %d\n",
                           inet_ntoa(address.sin_addr), ntohs(address.sin_port));

                    close(sd);
                } else if (valread > 0) {
                    buffer[valread] = '\0';
                    printf("%s\n", buffer);

                    char method[16], path[256], version[16];
                    if (sscanf(buffer, "%15s %255s %15s", method, path, version) == 3) {
                        handle_request(sd, method, path, NULL);
                    } else {
                        const char *response = "HTTP/1.1 400 Bad Request\nContent-Type: text/plain\nContent-Length: 11\n\nBad Request";
                        send(sd, response, strlen(response), 0);
                        close(sd);
                    }

                    EV_SET(&change_event, sd, EVFILT_READ, EV_ADD | EV_ENABLE, 0, 0, NULL);
                    if (kevent(kq, &change_event, 1, NULL, 0, NULL) == -1) {
                        perror("kevent");
                        close(sd);
                    }
                }
            }
        }
    }

    cleanup(server_fd, kq);
    return 0;
}

