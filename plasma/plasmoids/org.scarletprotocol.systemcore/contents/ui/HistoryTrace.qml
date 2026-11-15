import QtQuick

Canvas {
    id: trace
    property var readings: []
    property color ink: "#e41951"

    function append(value) {
        const next = readings.slice(-31)
        next.push(value)
        readings = next
    }

    onReadingsChanged: requestPaint()
    onInkChanged: requestPaint()
    onPaint: {
        const ctx = getContext("2d")
        ctx.clearRect(0, 0, width, height)
        ctx.strokeStyle = ink
        ctx.lineJoin = "round"
        ctx.lineWidth = 1.5
        ctx.beginPath()
        let connected = false
        for (let i = 0; i < readings.length; ++i) {
            if (readings[i] === null) {
                connected = false
                continue
            }
            const x = 1 + (width - 2) * (32 - readings.length + i) / 31
            const y = height - 1 - (height - 2) * Math.min(100, Math.max(0, readings[i])) / 100
            if (connected) ctx.lineTo(x, y)
            else ctx.moveTo(x, y)
            connected = true
        }
        ctx.stroke()
    }
}
