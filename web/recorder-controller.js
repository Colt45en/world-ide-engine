/**
 * RecorderController - Audio/video capture with timeline markers
 */

class RecorderController {
    constructor() {
        this.statusElement = document.getElementById('recorder-state');
        this.markersElement = document.getElementById('timeline-markers');
        this.recording = false;
        this.startTime = null;
        this.markers = [];

        // Listen to bridge events
        studioBridge.on('chat:record', (data) => {
            if (data.action === 'start') this.startRecording();
            if (data.action === 'stop') this.stopRecording();
        });
        studioBridge.on('chat:marker', (data) => {
            this.addMarker(data.label);
        });
        studioBridge.on('engine:analyzed', (data) => {
            if (this.recording) {
                this.addMarker(`Analysis: ${data.sentiment_score.toFixed(2)}`);
            }
        });
    }

    startRecording() {
        if (this.recording) return;

        this.recording = true;
        this.startTime = Date.now();
        this.markers = [];
        this.updateStatus('Recording');
        this.updateMarkers();

        studioBridge.emit('recorder:started', { timestamp: this.startTime });
    }

    stopRecording() {
        if (!this.recording) return;

        this.recording = false;
        const duration = Date.now() - this.startTime;
        this.updateStatus('Idle');

        studioBridge.emit('recorder:stopped', {
            duration,
            markers: this.markers
        });
    }

    addMarker(label = 'Marker') {
        if (!this.recording) {
            this.updateStatus('Not recording - start recording first');
            return;
        }

        const timestamp = Date.now() - this.startTime;
        const marker = {
            label,
            timestamp,
            time: this.formatTime(timestamp)
        };

        this.markers.push(marker);
        this.updateMarkers();

        studioBridge.emit('recorder:marker', marker);
    }

    updateStatus(status) {
        this.statusElement.textContent = status;
    }

    updateMarkers() {
        if (this.markers.length === 0) {
            this.markersElement.innerHTML = '<p style="color: #888; font-size: 12px;">No markers yet</p>';
            return;
        }

        this.markersElement.innerHTML = this.markers
            .map(m => `
                <div class="timeline-marker">
                    <strong>${m.time}</strong> - ${m.label}
                </div>
            `)
            .join('');
    }

    formatTime(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
}

// Initialize controller
const recorderController = new RecorderController();
