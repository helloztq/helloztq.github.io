---
layout: default
---

good
good
good
<h1>Hello jekyll</h1>
<p>This is the index page</p>
<p>My post list:</p>
<ul>
   {% for post in site.posts %}
       <li><a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a></li>
   {% endfor %}


</ul>