import yaml
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist
from markdown import markdown
from thisisthebus.settings.constants import FRONTEND_DIR, DATA_DIR


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

        context['body_text'] = markdown(page_yaml['body_text'])
    except FileNotFoundError:
        # There is no yaml for this page. That's OK.
        pass

    # Let's see if there's a special template for this page.
    try:
        template = get_template('page_specific/%s' % full_page_name)
    except TemplateDoesNotExist:
        template = get_template('shared/generic-page.html')

    html = template.render(context)

    with open("%s/%s" % (FRONTEND_DIR, filename), "w+") as f:
        f.write(html)