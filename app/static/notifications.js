function receive_message(message, user_id, display_name, notification_html) {
    const template = document.createElement('template')
    template.innerHTML = notification_html
    const el = template.content.children[0]
    document.getElementById('notifications-list').prepend(el)

    window.setTimeout(() => {
        el.classList.add('fadeout')
    }, 5000)

    el.addEventListener('transitionend', () => {
        el.remove()
    })
}

