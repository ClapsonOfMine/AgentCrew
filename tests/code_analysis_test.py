from AgentCrew.modules.code_analysis import CodeAnalysisService


if __name__ == "__main__":
    analyze = CodeAnalysisService()
    result = analyze.analyze_code_structure(
        "/home/quytruong/source/github.com/greyball-team/greyball-mono/apps/main-app/",
        exclude_patterns=["public/**"],
    )
    print(result)
