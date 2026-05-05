---
layout: default
---

<h1>{{page.title}}</h1>

{% if page.image != blank %}
<img src="{{site.baseurl}}/assets/images/{{page.image}}"></img>
{% endif %}

{{content}}
