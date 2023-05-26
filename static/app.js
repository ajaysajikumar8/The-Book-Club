class Chatbox {
	constructor() {
		this.arguments = {
			openButton: document.querySelector(".chatbox__button"),
			chatBox: document.querySelector(".chatbox__support"),
			sendButton: document.querySelector(".send__button"),
		};

		this.state = false;
		this.messages = [];
	}

	display() {
		const { openButton, chatBox, sendButton } = this.arguments;

		openButton.addEventListener("click", () => this.toggleState(chatBox));

		sendButton.addEventListener("click", () => this.onSendButton(chatBox));

		const node = chatBox.querySelector("input");
		node.addEventListener("keyup", ({ key }) => {
			if (key === "Enter") {
				this.onSendButton(chatBox);
			}
		});
	}

	toggleState(chatbox) {
		this.state = !this.state;

		if (this.state) {
			chatbox.classList.add("chatbox--active");
		} else {
			chatbox.classList.remove("chatbox--active");
		}
	}

	onSendButton(chatbox) {
		var textField = chatbox.querySelector("input");
		let text = textField.value;
		if (text === "") {
			return;
		}

		let message = { name: "User", message: text };
		this.messages.push(message);

		fetch($SCRIPT_ROOT + "/predict", {
			method: "POST",
			body: JSON.stringify({ message: text }),
			mode: "cors",
			headers: {
				"Content-Type": "application/json",
			},
		})
			.then((response) => response.json())
			.then((data) => {
				let responseMessage = { name: "Amanda", message: data.answer };
				this.messages.push(responseMessage);
				this.updateChatText(chatbox);
				textField.value = "";
			})
			.catch((error) => {
				console.error("Error:", error);
				this.updateChatText(chatbox);
				textField.value = "";
			});
	}

	updateChatText(chatbox) {
		var html = "";
		this.messages
			.slice()
			.reverse()
			.forEach(function (item, index) {
				if (item.name === "Amanda") {
					html +=
						"<div class='messages__item messages__item--visitor'>" +
						item.message +
						"</div>";
				} else {
					html +=
						"<div class='messages__item messages__item--operator'>" +
						item.message +
						"</div>";
				}
			});

		const chatmessage = chatbox.querySelector(".chatbox__messages");
		chatmessage.innerHTML = html;
	}
}

const chatbox = new Chatbox();
chatbox.display();





