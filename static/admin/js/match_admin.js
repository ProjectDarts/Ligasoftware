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
});