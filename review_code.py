from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

openai.api_key = "sk-proj-1P9qdaE11afpGTuyVd38T3BlbkFJGYWh5QKiWqJsBfmay5ll"

@app.route('/api/compare', methods=['POST'])
def compare_code():
    data = request.get_json()
    pr_content = data["pr_content"]
    branch = data.get("branch", "main")

    main_content = get_main_branch_content(branch)

    review_comments = []
    for file_path, pr_code in pr_content.items():
        main_code = main_content.get(file_path, "")
        prompt = f"""
        Review the following Pull Request for code quality, style, and best practices. Provide detailed feedback and suggestions for improvement.

        PR Content:
        {pr_code}

        Existing Code on {branch}:
        {main_code}

        Focus on the following aspects:
        1. Code readability and maintainability.
        2. Potential bugs and logical errors.
        3. Compliance with coding standards and best practices.
        4. Efficiency and performance improvements.

        Provide your review below:
        """
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=prompt,
            max_tokens=500
        )
        review_comments.append({
            "file": file_path,
            "review": response.choices[0].text
        })

    return jsonify(review_comments)

def get_main_branch_content(branch):
    # Implement this function to fetch the main branch content
    pass

if __name__ == '__main__':
    app.run(debug=True)

