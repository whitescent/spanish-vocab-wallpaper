$(document).ready(function() {
    $(document).on("mouseenter", ".card-wrap", function() {
        $(this).find("article").slideDown("fast");
    });
    $(document).on("mouseleave", ".card-wrap", function() {
        $(this).find("article").slideUp("fast");
    });
});

function loadWords(words, clear = true) {
    var dict = JSON.parse(words);
    var container = $(".container");
    if(clear)
        container.find(".card-wrap:not(.template)").remove();
    for(var i of dict) {
        var card = $(".card-wrap.template").clone();
        card.removeClass("template");
        card.find(".card-word").text(i.word);
        card.find(".card-cara").text(i.cara);
        var exps = card.find(".card-exps");
        if(i.exp) {
            for(var j of i.exp)
                exps.append("<li>" + j + "</li>")
        }
        i.eg && exps.append("<li>" + i.eg + "</li>");
        container.append(card);
    }
}

function loadSentence(sentence, translation) {
    $(".sen").text(sentence + " / " + translation);
}
