"use strict";

/*
 * Astra AI — Customer Assistant
 * Frontend interaction layer
 */

class CustomerAssistant {
    constructor() {
        this.elements = this.getElements();

        this.isSending = false;

        // Unique session ID for this browser tab
        this.sessionId = this.getSessionId();

        this.initialize();
    }


    getElements() {
        return {
            chatForm: document.getElementById("chatForm"),
            messageInput: document.getElementById("messageInput"),
            sendButton: document.getElementById("sendButton"),
            chatMessages: document.getElementById("chatMessages"),
            typingIndicator: document.getElementById("typingIndicator"),
            characterCount: document.getElementById("characterCount"),

            clearChat: document.getElementById("clearChat"),

            appointmentModal:
                document.getElementById("appointmentModal"),

            closeAppointment:
                document.getElementById("closeAppointment"),

            appointmentForm:
                document.getElementById("appointmentForm"),

            appointmentDate:
                document.getElementById("appointmentDate")
        };
    }


    /*
     * Creates a unique ID for the conversation.
     */

    createSessionId() {

        if (
            window.crypto &&
            typeof window.crypto.randomUUID === "function"
        ) {
            return window.crypto.randomUUID();
        }

        return (
            "session-" +
            Date.now() +
            "-" +
            Math.random()
                .toString(36)
                .substring(2, 12)
        );
    }


    /*
     * Gets the existing session ID.
     * If there isn't one, creates a new one.
     */

    getSessionId() {

        let sessionId =
            sessionStorage.getItem(
                "astra_session_id"
            );

        if (!sessionId) {

            sessionId =
                this.createSessionId();

            sessionStorage.setItem(
                "astra_session_id",
                sessionId
            );
        }

        return sessionId;
    }


    /*
     * Starts a completely new conversation.
     */

    startNewSession() {

        this.sessionId =
            this.createSessionId();

        sessionStorage.setItem(
            "astra_session_id",
            this.sessionId
        );
    }


    initialize() {

        this.bindEvents();

        this.setMinimumAppointmentDate();

        this.autoResizeInput();
    }


    bindEvents() {

        /*
         * Main chat form
         */

        this.elements.chatForm.addEventListener(
            "submit",
            (event) => {

                event.preventDefault();

                this.handleMessageSubmit();
            }
        );


        /*
         * Enter = send
         * Shift + Enter = new line
         */

        this.elements.messageInput.addEventListener(
            "keydown",
            (event) => {

                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    this.handleMessageSubmit();
                }
            }
        );


        /*
         * Character counter
         */

        this.elements.messageInput.addEventListener(
            "input",
            () => {

                this.updateCharacterCount();

                this.autoResizeInput();
            }
        );


        /*
         * Quick actions
         */

        document
            .querySelectorAll("[data-message]")
            .forEach((button) => {

                button.addEventListener(
                    "click",
                    () => {

                        const message =
                            button.dataset.message;

                        this.sendQuickMessage(
                            message
                        );
                    }
                );
            });


        /*
         * Appointment buttons
         */

        document
            .querySelectorAll(
                '[data-action="appointment"]'
            )
            .forEach((button) => {

                button.addEventListener(
                    "click",
                    () => {

                        this.openAppointmentModal();
                    }
                );
            });


        /*
         * Modal
         */

        this.elements.closeAppointment.addEventListener(
            "click",
            () => {

                this.closeAppointmentModal();
            }
        );


        /*
         * Close modal by clicking outside
         */

        this.elements.appointmentModal.addEventListener(
            "click",
            (event) => {

                if (
                    event.target ===
                    this.elements.appointmentModal
                ) {

                    this.closeAppointmentModal();
                }
            }
        );


        /*
         * Escape closes modal
         */

        document.addEventListener(
            "keydown",
            (event) => {

                if (
                    event.key === "Escape" &&
                    this.elements.appointmentModal.classList.contains(
                        "active"
                    )
                ) {

                    this.closeAppointmentModal();
                }
            }
        );


        /*
         * Appointment form
         */

        this.elements.appointmentForm.addEventListener(
            "submit",
            (event) => {

                event.preventDefault();

                this.handleAppointmentSubmit();
            }
        );


        /*
         * Clear chat
         */

        this.elements.clearChat.addEventListener(
            "click",
            () => {

                this.clearConversation();
            }
        );
    }


    async handleMessageSubmit() {

        if (this.isSending) {
            return;
        }


        const message =
            this.elements.messageInput.value.trim();


        if (!message) {
            return;
        }


        this.addUserMessage(message);


        this.elements.messageInput.value = "";


        this.updateCharacterCount();


        this.resetInputHeight();


        this.setSendingState(true);


        this.showTyping();


        try {

            /*
             * Send message + session ID
             * to Flask backend.
             */

            const response =
                await fetch(
                    "/api/chat",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                message: message,

                                session_id:
                                    this.sessionId
                            })
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Unable to contact the server."
                );
            }


            const data =
                await response.json();


            this.hideTyping();


            const reply =
                data.reply ||
                "I'm sorry, I couldn't process your request.";


            this.addAssistantMessage(reply);


        } catch (error) {

            console.error(
                "Chat request failed:",
                error
            );


            this.hideTyping();


            this.addAssistantMessage(
                "I'm having trouble connecting right now. Please try again in a moment."
            );


        } finally {

            this.setSendingState(false);

            this.elements.messageInput.focus();
        }
    }


    sendQuickMessage(message) {

        if (this.isSending) {
            return;
        }


        this.elements.messageInput.value =
            message;


        this.updateCharacterCount();


        this.handleMessageSubmit();
    }


    addUserMessage(message) {

        const wrapper =
            document.createElement("div");


        wrapper.className =
            "message user-message";


        wrapper.innerHTML = `
            <div class="message-content">

                <div class="message-bubble">
                    ${this.escapeHtml(message)}
                </div>

                <div class="message-time">
                    Just now
                </div>

            </div>

            <div class="message-avatar">
                You
            </div>
        `;


        this.elements.chatMessages.appendChild(
            wrapper
        );


        this.scrollToBottom();
    }


    addAssistantMessage(message) {

        const wrapper =
            document.createElement("div");


        wrapper.className =
            "message assistant-message";


        wrapper.innerHTML = `
            <div class="message-avatar">
                ✦
            </div>

            <div class="message-content">

                <div class="message-name">
                    Astra AI
                </div>

                <div class="message-bubble">
                    ${this.formatAssistantMessage(message)}
                </div>

                <div class="message-time">
                    Just now
                </div>

            </div>
        `;


        this.elements.chatMessages.appendChild(
            wrapper
        );


        this.scrollToBottom();
    }


    formatAssistantMessage(message) {

        return this.escapeHtml(message)
            .replace(/\n/g, "<br>");
    }


    escapeHtml(value) {

        const div =
            document.createElement("div");


        div.textContent = value;


        return div.innerHTML;
    }


    showTyping() {

        this.elements.typingIndicator.classList.add(
            "active"
        );


        this.scrollToBottom();
    }


    hideTyping() {

        this.elements.typingIndicator.classList.remove(
            "active"
        );
    }


    setSendingState(isSending) {

        this.isSending = isSending;


        this.elements.sendButton.disabled =
            isSending;


        this.elements.messageInput.disabled =
            isSending;
    }


    updateCharacterCount() {

        const length =
            this.elements.messageInput.value.length;


        this.elements.characterCount.textContent =
            `${length} / 2000`;
    }


    autoResizeInput() {

        const input =
            this.elements.messageInput;


        input.style.height =
            "auto";


        input.style.height =
            `${Math.min(input.scrollHeight, 130)}px`;
    }


    resetInputHeight() {

        this.elements.messageInput.style.height =
            "auto";
    }


    scrollToBottom() {

        requestAnimationFrame(() => {

            this.elements.chatMessages.scrollTop =
                this.elements.chatMessages.scrollHeight;

        });
    }


    openAppointmentModal() {

        this.elements.appointmentModal.classList.add(
            "active"
        );


        document.body.style.overflow =
            "hidden";


        this.elements.appointmentForm
            .querySelector("input")
            ?.focus();
    }


    closeAppointmentModal() {

        this.elements.appointmentModal.classList.remove(
            "active"
        );


        document.body.style.overflow =
            "";
    }


    setMinimumAppointmentDate() {

        if (!this.elements.appointmentDate) {
            return;
        }


        const today =
            new Date();


        const year =
            today.getFullYear();


        const month =
            String(
                today.getMonth() + 1
            ).padStart(2, "0");


        const day =
            String(
                today.getDate()
            ).padStart(2, "0");


        this.elements.appointmentDate.min =
            `${year}-${month}-${day}`;
    }


    async handleAppointmentSubmit() {

        const form =
            this.elements.appointmentForm;


        const formData =
            new FormData(form);


        const appointment =
            Object.fromEntries(
                formData.entries()
            );


        if (
            !appointment.name ||
            !appointment.email ||
            !appointment.date ||
            !appointment.time
        ) {

            return;
        }


        const submitButton =
            form.querySelector(
                ".appointment-submit"
            );


        const originalText =
            submitButton.innerHTML;


        submitButton.disabled =
            true;


        submitButton.innerHTML =
            "<span>Booking...</span>";


        try {

            /*
             * Flask backend processes
             * the appointment.
             */

            const response =
                await fetch(
                    "/api/appointments",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                appointment
                            )
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Appointment booking failed."
                );
            }


            const data =
                await response.json();


            this.closeAppointmentModal();


            form.reset();


            this.addAssistantMessage(
                data.message ||
                "Your appointment request has been received. We'll be in touch shortly."
            );


        } catch (error) {

            console.error(
                "Appointment error:",
                error
            );


            alert(
                "We couldn't book the appointment right now. Please try again."
            );


        } finally {

            submitButton.disabled =
                false;


            submitButton.innerHTML =
                originalText;
        }
    }


    clearConversation() {

        const messages =
            this.elements.chatMessages
                .querySelectorAll(".message");


        messages.forEach(
            (message) => message.remove()
        );


        /*
         * Start a completely new
         * backend conversation.
         */

        this.startNewSession();


        this.addAssistantMessage(
            "Hi! 👋 I'm Astra, your AI customer assistant. How can I help you today?"
        );
    }
}


/*
 * Start application after DOM is ready.
 */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        window.customerAssistant =
            new CustomerAssistant();

    }
);