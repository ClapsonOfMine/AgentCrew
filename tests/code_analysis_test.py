from AgentCrew.modules.code_analysis import CodeAnalysisService


if __name__ == "__main__":
    analyze = CodeAnalysisService()
    result = analyze.analyze_code_structure(
        "/home/quytruong/source/github.com/greyball-team/greyball-mono/apps/genai",
        exclude_patterns=[
            "**/public/**",
            "**/test/**",
            "**/tests/**",
            "**/assets/**",
            "**/__pycache__/**",
            "**/.pytest_cache/**",
            "**/node_modules/**",
            "**/*.pyc",
            "**/*.pyo",
            "**/*.pyd",
        ],
    )
    print(result)
