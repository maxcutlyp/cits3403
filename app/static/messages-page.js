const talking_to_or_null = () => {
    const to = Number.parseInt(window.location.pathname.split('/').pop())
    if (Number.isNaN(to)) {
        return null
    }

    return to
}

const talking_to = () => {
    const to = talking_to_or_null()
    if (to === null) {
        throw new Error('Couldn\'t get user ID from URL.')
    }

    return to
}

const send_message_from_input = async () => {
    const message_input = document.getElementById('message-input')
    const message = message_input.textContent

    if (message.length <= 0) {
        return
    }

    var currentDate = new Date();

    var hours = currentDate.getHours();
    var minutes = currentDate.getMinutes();

    add_message_to_chat(false, message, hours + ":" + minutes)

    await send_message(message, talking_to(), update_sidebar)

    message_input.textContent = ''
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

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('send-btn')?.addEventListener('click', send_message_from_input)
    const message_input = document.getElementById('message-input')
    if (message_input) {
        message_input.addEventListener('keydown', e => {
            if (e.key === 'Enter' && e.ctrlKey) {
                send_message_from_input()
            }
        })

        message_input.addEventListener('input', e => {
            if (e.target.textContent === '') {
                // Get rid of the pesky <br> that prevents it from being :empty
                e.target.lastElementChild?.remove()
            }
        })

        message_input.addEventListener('paste', e => {
            if (e.clipboardData.files.length) {
                e.preventDefault()
                // TODO: Add to attachments
                console.log("file(s) pasted")
            }
        })
    }

    // notifications.js will be loaded before this script. Its receive_message
    // will be overwritten by ours, but we actually want to keep it around so we
    // can use it if the user gets a message that isn't from the conversation
    // they're currently looking at. Yes, this is very scuffed.
    const receive_message_as_notification = window.receive_message

    window.receive_message = (message, user_id, display_name, notification_html) => {
        update_sidebar() // don't await, let it run in the background

        if (user_id !== talking_to_or_null()) {
            receive_message_as_notification(message, user_id, display_name, notification_html)
            return
        }

        var currentDate = new Date();

        var hours = currentDate.getHours();
        var minutes = currentDate.getMinutes();

        add_message_to_chat(true, message, hours + ":" + minutes)
    }
})
