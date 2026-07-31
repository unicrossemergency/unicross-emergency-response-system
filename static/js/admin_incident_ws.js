document.addEventListener("DOMContentLoaded", function () {

    // ================= WEBSOCKET =================
    const socket = new WebSocket(
        "ws://127.0.0.1:8000/ws/incidents/"
    );

    // ================= SOUND =================
    const alertSound = new Audio(
        "/static/sounds/emergency.mp3"
    );

    alertSound.preload = "auto";
    alertSound.volume = 1.0;

    let soundArmed = false;


    // ================= ARM SOUND SYSTEM =================
    function armSoundSystem() {

        if (soundArmed) return;

        alertSound.play()

        .then(() => {

            alertSound.pause();
            alertSound.currentTime = 0;

            soundArmed = true;

            console.log(
                "🔊 Sound system ARMED"
            );

            // Remove button after activation
            const btn = document.getElementById(
                "enableSoundBtn"
            );

            if (btn) btn.remove();

        })

        .catch(err => {
            console.log(
                "Sound arm failed:",
                err
            );
        });
    }


    // ================= AUTO ARM EVENTS =================
    ["click", "keydown", "touchstart"]
    .forEach(event => {

        document.addEventListener(
            event,
            armSoundSystem
        );

    });


    // ================= PLAY SOUND =================
    function playSound() {

        if (!soundArmed) {

            console.log(
                "🔇 Sound not armed yet"
            );

            return;
        }

        alertSound.pause();
        alertSound.currentTime = 0;

        alertSound.play()

        .catch(err => {

            console.log(
                "Playback blocked:",
                err
            );

        });
    }


    // ================= ALERT POPUP =================
    function showAlert(data) {

        const box = document.createElement(
            "div"
        );

        box.innerHTML = `
            <strong>
                🚨 ${data.type.toUpperCase()} INCIDENT
            </strong><br>

            <small>
                ${data.description}
            </small><br>

            <small>
                <b>Location:</b>
                ${data.location || "Unknown"}
            </small>
        `;


        Object.assign(box.style, {

            position: "fixed",
            top: "20px",
            right: "20px",

            background: "#dc3545",
            color: "white",

            padding: "15px",
            borderRadius: "10px",

            zIndex: "99999",

            width: "300px",

            boxShadow:
                "0 0 10px rgba(0,0,0,0.3)",

            fontFamily: "Arial",
            animation:
                "fadeIn 0.3s ease-in-out"

        });

        document.body.appendChild(
            box
        );

        setTimeout(() => {
            box.remove();
        }, 10000);
    }


    // ================= TITLE FLASH =================
    function flashTitle() {

        const original =
            document.title;

        let count = 0;

        const interval =
            setInterval(() => {

                document.title =
                    count % 2 === 0
                    ? "🚨 NEW INCIDENT!"
                    : original;

                count++;

                if (count > 10) {

                    clearInterval(
                        interval
                    );

                    document.title =
                        original;
                }

            }, 500);
    }


    // ================= ENABLE BUTTON =================
    function createEnableSoundButton() {

        const btn =
            document.createElement(
                "div"
            );

        btn.id =
            "enableSoundBtn";

        btn.innerText =
            "🔊 Click to enable emergency alerts";

        Object.assign(btn.style, {

            position: "fixed",

            bottom: "20px",
            right: "20px",

            background: "#000",
            color: "#fff",

            padding: "10px 15px",

            borderRadius: "8px",

            cursor: "pointer",

            zIndex: "99999",

            fontSize: "14px"

        });

        btn.onclick =
            armSoundSystem;

        document.body.appendChild(
            btn
        );
    }


    createEnableSoundButton();


    // ================= WEBSOCKET EVENTS =================

    socket.onopen = function () {

        console.log(
            "✅ WebSocket connected"
        );

    };


    socket.onerror = function (error) {

        console.log(
            "❌ WebSocket error:",
            error
        );

    };


    socket.onclose = function () {

        console.log(
            "⚠️ WebSocket closed"
        );

    };


    socket.onmessage = function (event) {

        const data = JSON.parse(
            event.data
        );

        console.log(
            "📩 Received:",
            data
        );


        // ================= NEW INCIDENT =================
        if (
            data.message_type ===
            "new_incident"
        ) {

            showAlert(data);

            playSound();

            flashTitle();
        }


        // ================= STATUS UPDATE =================
        else if (
            data.message_type ===
            "status_update"
        ) {

            console.log(
                "🔥 Status updated:",
                data.status
            );
        }

    };

});