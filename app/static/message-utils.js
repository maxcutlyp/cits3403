/*

Include this file to use the messages API.

To receive messages, define a function named `receive_message`, like:

const receive_message = (message, user_id, display_name, notification_html) => { ... }
- message: string: text content of the received message
- user_id: int: ID of the sending user
- display_name: string: display name of the sending user
- notification_html: string: rendered HTML for a notification (for use with notifications.js)

To send messages, call `send_message(message, user_id, server_ack)`
- message: string: text content of the message to send
- user_id: int: ID of the user to send the message to
- server_ack (optional): function to be called when the server acknowledges the message (see https://socket.io/docs/v4/client-api/#socketemiteventname-args)

*/

let socket

const send_message = (message, user_id, server_ack) => {
    socket.emit('json',
        {
            'to': user_id,
            'message': message,
        },
        server_ack,
    )
}

document.addEventListener('DOMContentLoaded', () => {
    socket = io()
    socket.on('json', (data) => {
        if (typeof receive_message === 'function') {
            receive_message(data.message, data.from.id, data.from.display_name, data.notification_html)
        } else {
            console.log(`Received message, no handler: ${JSON.stringify(data)}`)
        }
    })
})
