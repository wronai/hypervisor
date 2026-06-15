# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/screenshot_analysis_agent.yaml
# Contract hash: sha256:a541c061b26d8303d14f931b3ad48dea9ada37990cc1a9426d2c1c0a13fbc77e

# ruff: noqa: E501

AGENT_CARD = {'name': 'screenshot-analysis-agent',
 'version': '0.1.0',
 'description': 'Analyze screenshot artifacts captured by desktop-operator and persist '
                'observations.',
 'generated_from': {'contract': 'contracts/agents/screenshot_analysis_agent.yaml',
                    'contract_hash': 'sha256:a541c061b26d8303d14f931b3ad48dea9ada37990cc1a9426d2c1c0a13fbc77e'},
 'capabilities': [{'name': 'analyze_screenshot',
                   'type': 'command',
                   'description': 'Analyze an artifact:// or file:// screenshot and '
                                  'append JSONL/Markdown observations.',
                   'uri': 'analysis://screenshots/analyze',
                   'output_schema': 'app.screenshots.v1.ScreenshotObservation',
                   'renderer': 'detail',
                   'command': 'AnalyzeScreenshot',
                   'input_schema': 'app.screenshots.v1.AnalyzeScreenshotCommand',
                   'emits': ['ScreenshotObservationRecorded']},
                  {'name': 'capture_and_analyze',
                   'type': 'command',
                   'description': 'Ask desktop-operator to capture a page, then '
                                  'analyze the returned artifact.',
                   'uri': 'workflow://screenshots/capture-and-analyze',
                   'output_schema': 'app.screenshots.v1.CaptureAndAnalysisResult',
                   'renderer': 'detail',
                   'command': 'CaptureAndAnalyze',
                   'input_schema': 'app.screenshots.v1.CaptureAndAnalyzeCommand',
                   'emits': ['ScreenshotCaptured', 'ScreenshotObservationRecorded']},
                  {'name': 'scheduled_capture_analysis',
                   'type': 'command',
                   'description': 'Host schedule hook for running capture_and_analyze '
                                  'every five minutes.',
                   'uri': 'cron://screenshots/capture-analysis/every-5-min',
                   'output_schema': 'app.screenshots.v1.CaptureAndAnalysisResult',
                   'renderer': 'detail',
                   'command': 'RunScheduledCaptureAnalysis',
                   'input_schema': 'app.screenshots.v1.CaptureAndAnalyzeCommand',
                   'emits': ['ScreenshotCaptureAnalysisTick']}]}
