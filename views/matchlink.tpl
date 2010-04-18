% if len(matches) == 1:
    <li><a href="#{{id}}">one matched {{field}}</a></li>
% elif matches:
    <li><a href="#{{id}}">{{len(matches)}} matched {{field}}</a></li>
% end
