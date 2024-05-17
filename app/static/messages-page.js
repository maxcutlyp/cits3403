const talking_to = () => {
    const to = Number.parseInt(window.location.pathname.split('/').pop())
    if (Number.isNaN(to)) {
        throw new Error('Couldn\'t get user ID from URL.')
    }

    return to
}

const send_message_from_input = async () => {
    const message_input = document.getElementById('message-input')
    const message = message_input.value

    if (message.length <= 0) {
        return
    }

    var currentDate = new Date();

    var hours = currentDate.getHours();
    var minutes = currentDate.getMinutes();

    add_message_to_chat(false, message, hours + ":" + minutes)

    await send_message(message, talking_to(), update_sidebar)

    message_input.value = ''
}

const add_message_to_chat = (incoming, message, timestamp) => {
    // <p data-incoming|data-outgoing >
    //     <span class="msg-contents">${message}</span>
    //     <span class="msg-time">${timestamp}</span>
    // </p>

    const p = document.createElement('p')

    if (incoming) {
        p.dataset.incoming = ''
    } else {
        p.dataset.outgoing = ''
    }

    const msg_span = document.createElement('span')
    msg_span.textContent = message
    msg_span.classList.add("msg-contents")
    p.appendChild(msg_span)

    const time_span = document.createElement('span')
    time_span.textContent = timestamp
    time_span.classList.add("msg-time")
    p.appendChild(time_span)

    document.querySelector('.messages').prepend(p)
}

const update_sidebar = async () => {
    let query
    try {
        query = '?' + new URLSearchParams({ selected: talking_to() })
    } catch {
        query = ''
    }
    const resp = await fetch('/components/messages-sidebar' + query)

    if (!resp.ok) {
        alert('Failed to get recent messages.')
        return
    }

    document.getElementById('messages-sidebar').outerHTML = await resp.text()
}

function receive_message(message, user_id, display_name) {
    update_sidebar() // don't await, let it run in the background

    if (user_id !== talking_to()) {
        // TODO: notification?
        return
    }

    var currentDate = new Date();

    var hours = currentDate.getHours();
    var minutes = currentDate.getMinutes();

    add_message_to_chat(true, message, hours + ":" + minutes)
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('send-btn')?.addEventListener('click', send_message_from_input)
    document.getElementById('message-input')?.addEventListener('keydown', e => {
        if (e.key === 'Enter') {
            send_message_from_input()
        }
    })
})
