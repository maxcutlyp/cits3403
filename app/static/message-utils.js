/*

Include this file to use the messages API.

To receive messages, define a function named `receive_message`, like:

const receive_message = (
    message, // string: text content of the received message
    attachment_ids, // Array<int>: list of IDs of attachments for the message, can be accessed at /attachments/<id>
    user_id, // int: ID of the sending user
    display_name, // string: display name of the sending user
    notification_html, // string: rendered HTML for a notification (for use with notifications.js)
    message_html, // string: rendered HTML for a message (for use with messages-page.js)
) => { ... }

To send messages, call:

send_message(
    message, // string: text content of the message to send
    attachments // Iterable<File>: list of File objects to attach to the message,
    user_id, // int: ID of the user to send the message to
    server_ack, // function (optional): will called when the message has been sent
)

`server_ack` looks like this:

const server_ack = (
    message_html, // string: rendered HTML for a message (for use with messages-page.js)
) => { ... }

*/

let socket

const send_message = async (message, attachments, user_id, server_ack) => {
    let attachment_ids = []
    if (attachments && attachments.length) {
        const form = new FormData()
        for (const file of attachments) {
            form.append(file.name, file)
        }

        const resp = await fetch('/attachments', {
            method: 'POST',
            body: form,
        })

        attachment_ids = await resp.json()
    }

    socket.emit('json',
        {
            'to': user_id,
            'message': message,
            'attachments': attachment_ids,
        },
        server_ack,
    )
}

document.addEventListener('DOMContentLoaded', () => {
    socket = io()
    socket.on('json', (data) => {
        if (typeof receive_message === 'function') {
            receive_message(
                data.message,
                data.attachments,
                data.from.id,
                data.from.display_name,
                data.notification_html,
                data.message_html,
            )
        } else {
            console.log(`Received message, no handler: ${JSON.stringify(data)}`)
        }
    })
})
