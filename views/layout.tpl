<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-type" content="text/html; charset=utf-8">
% try:
<title>{{query}} - vlasisku</title>
% except NameError:
<title>vlasisku</title>
% end
<link rel="shortcut icon" href="/static/favicon-16.png">
<link rel="stylesheet" href="/static/blueprint/screen.css" type="text/css" media="screen, projection">
<link rel="stylesheet" href="/static/blueprint/print.css" type="text/css" media="print">
<!--[if lt IE 8]><link rel="stylesheet" href="/static/blueprint/ie.css" type="text/css" media="screen, projection"><![endif]-->
<link rel="stylesheet" href="/static/custom.css" type="text/css" media="screen, projection, print">
<link rel="search" type="application/opensearchdescription+xml" href="/opensearch" title="Lojban dictionary">
<script type="text/javascript">
<!--
    function search() {
        window.location = encodeURIComponent(document.getElementById('query').value);
        return false;
    }
//-->
</script>
</head>
<body>
<div class="container">

<div id="nav" class="span-6">
<ol>
    <li><a href="/" rel="index" accesskey="h">Home</a></li>
    <li><a href="https://bugs.launchpad.net/vlasisku/+filebug" title="Found a bug? Report it!" accesskey="b">Bugs</a></li>
</ol>
</div>

<div class="span-18 last">
<form action="" onsubmit="return search();" id="search" class="inline">
    <p>
    % try:
        <input type="text" value="{{query}}" size="30" id="query" accesskey="f" onfocus="this.select()">
    % except NameError:
        <input type="text" size="30" id="query" accesskey="f" onfocus="this.select()">
    % end
        <button type="submit"><img src="/static/favicon-16.png" alt=""> Find!</button>
    </p>
</form>
</div>

<script type="text/javascript">
<!--
    document.getElementById('query').focus();
//-->
</script>

<div class="clear"></div>
% include

</div>
</body>
</html>
