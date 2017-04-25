import maya
import yaml
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist
import markdown
from thisisthebus.settings.constants import FRONTEND_DIR, DATA_DIR
import hashlib
import json


def build_page(page_name, root=False, context=None, slicey=False):
    '''
    Takes a page name, checks to see if custom template or YAML files exist, writes HTML to frontend.
    '''
    context = context or {}
    context['slicey'] = slicey
    context['page_name'] = page_name
    if root:
        full_page_name = "root!%s.html" % page_name
        filename = "%s.html" % page_name
    else:
        full_page_name = "%s.html" % page_name
        filename = "pages/%s.html" % page_name


    try:
        yaml_filename = ("%s/authored/pages/%s" % (DATA_DIR, full_page_name)).replace(".html", ".yaml")

        with open(yaml_filename, "r") as f:
            page_yaml = yaml.load(f)

        context['author'] = page_yaml.get('author')
        context['title'] = page_yaml.get('title') or page_name
        context['body_text'] = markdown.markdown(page_yaml['body_text'], extensions=['markdown.extensions.tables'])

        page_checksum = hashlib.md5(json.dumps(context, sort_keys=True).encode()).hexdigest()

    except FileNotFoundError:
        # There is no yaml for this page. That's OK.
        pass
    else:

        try:
            json_meta_filename = ("%s/compiled/pages/%s.json" % (DATA_DIR, full_page_name)).rstrip(".html")
            with open(json_meta_filename, "r") as f:
                page_meta_json = json.loads(f.read())

            previous_page_checksum = page_meta_json['page_checksum']

        except FileNotFoundError:
            # There is no JSON meta for this page yet.
            previous_page_checksum = None

        if page_checksum == previous_page_checksum:
            # No need to rebuild this page; it hasn't changed.
            return
        else:
            context['build_time'] = maya.now().datetime(to_timezone='US/Eastern', naive=True)
            page_meta = {'page_checksum': page_checksum}

        with open(json_meta_filename, "w") as f:
            f.write(json.dumps(page_meta))



    # Let's see if there's a special template for this page.
    try:
        template = get_template('page_specific/%s' % full_page_name)
    except TemplateDoesNotExist:
        template = get_template('shared/generic-page.html')

    html = template.render(context)

    with open("%s/%s" % (FRONTEND_DIR, filename), "w+") as f:
        f.write(html)