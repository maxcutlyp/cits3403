const send_message = async () => {
    const message_input = document.getElementById('message-input')
    const message = message_input.value

    if (message.length <= 0) {
        return
    }

    // TODO: This will be a websocket message rather than a HTTP endpoint eventually
    const resp = await fetch(window.location + '/send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'message': message,
        }),
    })

    if (!resp.ok) {
        alert('Failed to send message')
        return
    }

    message_input.value = ''
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('send-btn').addEventListener('click', send_message)
    document.getElementById('message-input').addEventListener('keydown', e => {
        if (e.key === 'Enter') {
            send_message()
        }
    })
})
