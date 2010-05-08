% rebase layout showgrid=showgrid

<div id="types" class="span-6">
<h2>Types</h2>
<dl>
% for type, definition in types:
    <dt><a href="{{type}}">{{type}}</a></dt>
    <dd>{{definition}}</dd>
% end
</dl>
</div>

<div id="classes" class="span-18 last">
<h2>Grammatical classes</h2>
<p>
% for grammarclass in sorted(classes):
    % scale = scales.get(grammarclass, 0.7)
    % style = 'loud' if scale >= 1 else 'quiet'
    <a href="{{grammarclass}}" style="font-size: {{scale}}em" class="{{style}}">{{grammarclass}}</a>
% end
</p>
</div>
