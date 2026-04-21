# Real Hardware TODO

## Immediate adapter replacements needed

### perception adapter
Replace stub event injection with:
- camera feed ingestion
- detector/tracker binding
- identity hint tagging

### motion adapter
Replace stub movement envelopes with:
- real CERBERUS API command translation
- gait-compatible locomotion mapping
- feedback from robot state

### battery adapter
Replace mock battery drain with:
- real battery percentage/state from CERBERUS/GO2
- charging/docked signal
- battery fault handling

### audio adapter
Replace stub TTS/STT routing with:
- real speaker output
- real microphone input
- wake/attention logic as needed

### peer transport adapter
Replace transport simulation with:
- Bluetooth discovery/session
- Wi-Fi peer messages
- voice fallback events

## Required hardware validation
- follow best friend safely
- dock on low battery
- stop on safety event
- resume after clear
- peer ping + response
