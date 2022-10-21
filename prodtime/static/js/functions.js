function showAll() {
  var chexbox = document.getElementById("show-all");
  var all_hidden_cels = document.getElementsByClassName("td-hidden");
  var i;
  if (chexbox.checked === true) {
    for(i=0;i<all_hidden_cels.length;i++)
    {
      all_hidden_cels[i].style.display="table-cell";
    }
    document.getElementById("num").width="3%"
    document.getElementById("prod").width="12%"
    document.getElementById("print-form").width="10%"
    document.getElementById("price").width="5%"
    document.getElementById("count").width="5%"
    document.getElementById("unit").width="5%"
    document.getElementById("bonus").width="5%"
    document.getElementById("bonus-sum").width="5%"
    document.getElementById("tax").width="5%"
    document.getElementById("tax-sum").width="5%"
    document.getElementById("sum").width="5%"
    document.getElementById("count-days").width="5%"
    document.getElementById("equivalent").width="5%"
    document.getElementById("prod-time").width="10%"
    document.getElementById("factory-number").width="5%"
    document.getElementById("edit-number").width="3%"
    document.getElementById("finish").width="3%"
    document.getElementById("made").width="3%"
  } else {
    for(i=0;i<all_hidden_cels.length;i++)
    {
      all_hidden_cels[i].style.display="none";
    }
    document.getElementById("num").width="3%"
    document.getElementById("prod").width="15%"
    document.getElementById("print-form").width="12%"
    document.getElementById("price").width="8%"
    document.getElementById("count").width="5%"
    document.getElementById("unit").width="5%"
    document.getElementById("sum").width="9%"
    document.getElementById("count-days").width="8%"
    document.getElementById("equivalent").width="8%"
    document.getElementById("prod-time").width="10%"
    document.getElementById("factory-number").width="8%"
    document.getElementById("edit-number").width="3%"
    document.getElementById("finish").width="3%"
    document.getElementById("made").width="3%"
  }
}

function CopyToBuffer(id) {
    const copyText = document.getElementById(id);
    copyText.disabled = false;
    copyText.select();
    document.execCommand("copy");
    copyText.disabled = true;
}
