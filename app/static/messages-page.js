const attachments = new Set()

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

    await send_message(message, Array.from(attachments), talking_to(), (message_html) => {
        update_sidebar()
        add_message_to_chat(message_html)
    })

    message_input.textContent = ''
    attachments.clear()
    for (const li of document.querySelectorAll('#attachments > li')) {
        li.remove()
    }
}

const add_message_to_chat = (message_html) => {
    const template = document.createElement('template')
    template.innerHTML = message_html
    const el = template.content.children[0]
    document.querySelector('.messages').prepend(el)
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

const add_to_attachments = (file) => {
    // <li>
    //     <span>{filename}</span>
    //     <input type="button" value="x">
    // </li>

    attachments.add(file)

    const li = document.createElement('li')

    const fname_span = document.createElement('span')
    fname_span.innerText = file.name
    li.appendChild(fname_span)

    const delete_btn = document.createElement('input')
    delete_btn.type = 'button'
    delete_btn.value = 'x'
    delete_btn.addEventListener('click', () => {
        attachments.delete(file)
        li.remove()
    })
    li.appendChild(delete_btn)

    document.getElementById('attachments').appendChild(li)
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
                for (const file of e.clipboardData.files) {
                    add_to_attachments(file)
                }
            }
        })
    }

    document.getElementById('attach-btn').addEventListener('change', e => {
        for (const file of e.target.files) {
            add_to_attachments(file)
        }
        e.target.value = null
    })

    // notifications.js will be loaded before this script. Its receive_message
    // will be overwritten by ours, but we actually want to keep it around so we
    // can use it if the user gets a message that isn't from the conversation
    // they're currently looking at. Yes, this is very scuffed.
    const receive_message_as_notification = window.receive_message

    window.receive_message = (
        message,
        attachments,
        user_id,
        display_name,
        notification_html,
        message_html,
    ) => {
        update_sidebar() // don't await, let it run in the background

        if (user_id !== talking_to_or_null()) {
            receive_message_as_notification(
                message,
                attachments,
                user_id,
                display_name,
                notification_html,
                message_html,
            )
            return
        }

        add_message_to_chat(message_html)
    }
})
