% if entries:
<div id="{{id}}">
<h2>{{title}}</h2>
<dl>
% for entry in entries:
    <dt><a href="{{entry}}">{{entry}}</a></dt>
    <dd>{{entry.definition}}</dd>
% end
</dl>
<hr>
</div>
% end

