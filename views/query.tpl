% rebase layout query=query, debug=debug

<div id="matches">
<ol>
% include matchlink matches=glosses, id='gloss'
% include matchlink matches=affix, id='affix'
% include matchlink matches=classes, id='class', field='grammatical class'
% include matchlink matches=types, id='type'
% include matchlink matches=definitions, id='definition'
% include matchlink matches=notes, id='notes'
</ol>
</div>

% if entry:
<div id="entry">
<h1>
    {{entry}}
% if entry.grammarclass:
    <sub>
    % for grammarclass in entry.terminates:
        <a href="{{grammarclass}}">{{grammarclass}}</a>…
    % end
        <a href="{{entry.grammarclass}}">{{entry.grammarclass}}</a>
    % if entry.terminator:
        …<a href="{{entry.terminator}}">{{entry.terminator}}</a>
    % end
    </sub>
% end
% if entry.affixes:
    % hyphen = '<span class="hyphen">-</span>'
    <span class="affixes">{{hyphen}}{{hyphen.join(entry.affixes)}}{{hyphen}}</span>
% end
    <span class="type">{{entry.type}}</span>
</h1>
<p class="definition">{{entry.definition}}</p>
% if entry.notes:
<p class="notes">{{entry.notes}}</p>
% end
<ul class="links">
% for section, link in entry.cll:
    <li><a href="{{link}}" title="Relevant section in the reference grammar.">CLL {{section}}</a></li>
% end
    <li><a href="http://jbovlaste.lojban.org/dict/{{entry}}" title="This entry in the dictonary editor.">jbovlaste</a></li>
</ul>
<hr>
</div>
% end

% if glosses:
<div id="gloss">
<h2>These entries matched gloss:</h2>
<dl>
% for gloss in glosses:
    <dt>
        <a href="{{gloss.entry}}">{{gloss.entry}}</a>
    % if gloss.sense:
        in sense "{{gloss.sense}}"
    %end
    % if gloss.place:
        on place {{gloss.place}}
    % end
    </dt>
    <dd>{{gloss.entry.definition}}</dd>
% end
</dl>
<hr>
</div>
% end

% include entrylist entries=affix, id='affix', title='This entry matched affix form:'
% include entrylist entries=classes, id='class', title='These entries matched grammatical class:'
% include entrylist entries=types, id='type', title='These entries matched type:'
% include entrylist entries=definitions, id='definition', title='These entries matched definition:'
% include entrylist entries=notes, id='notes', title='These entries matched notes:'
