document.addEventListener("DOMContentLoaded", function () {
    const leagueField = document.getElementById("id_league");
    const matchdayField = document.getElementById("id_matchday");

    function reloadWithParams() {
        const url = new URL(window.location.href);

        if (leagueField && leagueField.value) {
            url.searchParams.set("league", leagueField.value);
        } else {
            url.searchParams.delete("league");
        }

        if (matchdayField && matchdayField.value) {
            url.searchParams.set("matchday", matchdayField.value);
        } else {
            url.searchParams.delete("matchday");
        }

        window.location.href = url.toString();
    }

    function syncStatPlayers() {
        const player1 = document.getElementById("id_player1");
        const player2 = document.getElementById("id_player2");

        if (!player1 || !player2) {
            return;
        }

        const statPlayerFields = Array.from(
            document.querySelectorAll("tr.dynamic-player_stats select[name$='-player'], tr.form-row select[name$='-player']")
        ).filter(function (select) {
            return select.id !== "id_player1" && select.id !== "id_player2";
        });

        if (statPlayerFields.length >= 1) {
            statPlayerFields[0].value = player1.value;
            addReadonlyPlayerName(statPlayerFields[0], player1);
        }

        if (statPlayerFields.length >= 2) {
            statPlayerFields[1].value = player2.value;
            addReadonlyPlayerName(statPlayerFields[1], player2);
        }
    }

    function addReadonlyPlayerName(statSelect, sourceSelect) {
        if (!statSelect || !sourceSelect) {
            return;
        }

        const selectedText = sourceSelect.options[sourceSelect.selectedIndex]
            ? sourceSelect.options[sourceSelect.selectedIndex].text
            : "";

        statSelect.style.display = "none";

        const relatedWrapper = statSelect.closest(".related-widget-wrapper");
        if (relatedWrapper) {
            relatedWrapper.querySelectorAll("a").forEach(function (link) {
                link.style.display = "none";
            });
        }

        let label = statSelect.parentElement.querySelector(".readonly-stat-player-name");

        if (!label) {
            label = document.createElement("strong");
            label.className = "readonly-stat-player-name";
            statSelect.parentElement.appendChild(label);
        }

        label.textContent = selectedText || "-";
    }

    if (leagueField) {
        leagueField.addEventListener("change", function () {
            if (matchdayField) {
                matchdayField.value = "";
            }
            reloadWithParams();
        });
    }

    if (matchdayField) {
        matchdayField.addEventListener("change", function () {
            reloadWithParams();
        });
    }

    const player1 = document.getElementById("id_player1");
    const player2 = document.getElementById("id_player2");

    if (player1) {
        player1.addEventListener("change", syncStatPlayers);
    }

    if (player2) {
        player2.addEventListener("change", syncStatPlayers);
    }

    setTimeout(syncStatPlayers, 300);
});