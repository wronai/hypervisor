from __future__ import annotations

AGENT_CARD = {
    "name": "screenshot-analysis-agent",
    "version": "0.1.0",
    "description": (
        "Analyzes screenshot artifacts captured by desktop-operator and writes "
        "observations to output/analysis/screenshots."
    ),
    "generated_from": {
        "contract": "contracts/agents/screenshot_analysis_agent.yaml",
    },
    "capabilities": [
        {
            "name": "analyze_screenshot",
            "type": "command",
            "description": (
                "Analyze an artifact:// or file:// screenshot and append "
                "JSONL/Markdown observations."
            ),
            "uri": "analysis://screenshots/analyze",
            "command": "AnalyzeScreenshot",
            "input_schema": "app.screenshots.v1.AnalyzeScreenshotCommand",
            "output_schema": "app.screenshots.v1.ScreenshotObservation",
            "renderer": "detail",
            "emits": ["ScreenshotObservationRecorded"],
        },
        {
            "name": "capture_and_analyze",
            "type": "command",
            "description": (
                "Ask desktop-operator to capture a page, then analyze the "
                "returned artifact."
            ),
            "uri": "workflow://screenshots/capture-and-analyze",
            "command": "CaptureAndAnalyze",
            "input_schema": "app.screenshots.v1.CaptureAndAnalyzeCommand",
            "output_schema": "app.screenshots.v1.CaptureAndAnalysisResult",
            "renderer": "detail",
            "emits": ["ScreenshotCaptured", "ScreenshotObservationRecorded"],
        },
        {
            "name": "scheduled_capture_analysis",
            "type": "command",
            "description": "Host schedule hook for running capture_and_analyze every five minutes.",
            "uri": "cron://screenshots/capture-analysis/every-5-min",
            "command": "RunScheduledCaptureAnalysis",
            "input_schema": "app.screenshots.v1.CaptureAndAnalyzeCommand",
            "output_schema": "app.screenshots.v1.CaptureAndAnalysisResult",
            "renderer": "detail",
            "emits": ["ScreenshotCaptureAnalysisTick"],
        },
    ],
}

