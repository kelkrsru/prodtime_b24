function showAll() {
  var chexbox = document.getElementById("show-all");
  var all_hidden_cels = document.getElementsByClassName("td-hidden");
  if (chexbox.checked == true) {
    for(var i=0;i<all_hidden_cels.length;i++)
    {
      all_hidden_cels[i].style.display="table-cell";
    }
    document.getElementById("num").width="5%"
    document.getElementById("prod").width="15%"
    document.getElementById("print-form").width="15%"
    document.getElementById("price").width="5%"
    document.getElementById("count").width="5%"
    document.getElementById("unit").width="5%"
    document.getElementById("bonus").width="5%"
    document.getElementById("bonus-sum").width="5%"
    document.getElementById("tax").width="5%"
    document.getElementById("tax-sum").width="5%"
    document.getElementById("sum").width="5%"
    document.getElementById("count-days").width="10%"
    document.getElementById("prod-time").width="10%"
    document.getElementById("finish").width="5%"
  } else {
    for(var i=0;i<all_hidden_cels.length;i++)
    {
      all_hidden_cels[i].style.display="none";
    }
    document.getElementById("num").width="5%"
    document.getElementById("prod").width="20%"
    document.getElementById("print-form").width="20%"
    document.getElementById("price").width="10%"
    document.getElementById("count").width="5%"
    document.getElementById("unit").width="5%"
    document.getElementById("sum").width="10%"
    document.getElementById("count-days").width="10%"
    document.getElementById("prod-time").width="10%"
    document.getElementById("finish").width="5%"
  }
}

function CopyToBuffer(id) {
    const copyText = document.getElementById(id);
    copyText.disabled = false;
    copyText.select();
    document.execCommand("copy");
    copyText.disabled = true;
}
