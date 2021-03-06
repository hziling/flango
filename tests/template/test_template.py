import unittest
import os

from flango.template import Template, TemplateException, Loader


class LoaderTest(unittest.TestCase):
    def test_loader_with_no_file(self):
        loader = Loader()
        self.assertRaises(TemplateException, loader.load, 'hello.html')


class BaseTest(unittest.TestCase):

    def test_variable(self):
        rendered = Template('''
            hello, {{ name }}
            ''').render(name='flango')
        self.assertEqual(rendered, '''
            hello, flango
            ''')

    def test_for(self):
        rendered = Template('''
            {%for i in [1, 2, 3]%}
                {{ i }}
            {% endfor%}
            ''').render()
        self.assertEqual(rendered, '''
                1
                2
                3
            ''')

    def test_for_with_args(self):
        rendered = Template('''
            {% for i in l %}
                {{ i }}
            {% endfor %}
            ''').render(l=[1, 2, 3])
        self.assertEqual(rendered, '''
                1
                2
                3
            ''')

    def test_if_else(self):
        t = Template('''
            {% if i > 3 %}
            {{ i }}
            {% else %}
            less than 3
            {% endif %}
            ''')
        _p = t.render(i=2)
        _s = t.render(i=4)
        self.assertEqual(_p, '''
            less than 3
            ''')
        self.assertEqual(_s, '''
            4
            ''')

    def test_elif(self):
        t1 = Template('{% if 2 > 3 %}2{% elif 3 > 2 %}3{% else %}1').render()
        self.assertEqual(t1, '3')
        t2 = Template('{% if 2 > 3 %}2{% elif 3 < 2 %}3{% else %}0').render()
        self.assertEqual(t2, '0')

    def test_user_define_object(self):
        class A(object):

            def __init__(self, a, b):
                self.a = a
                self.b = b

        o = A("I am o.a", [1, 2, 3])
        rendered = Template('''
            {{ o.a }}
            {% for i in o.b %}
            {{ i }}
            {% endfor %}
            ''').render(o=o)
        self.assertEqual(rendered, '''
            I am o.a
            1
            2
            3
            ''')

    def test_nested_for_if(self):
        rendered = Template('''
            {% for i in l %}
                {% if i > 3 %}
                {{ i }}
                {% else %}
                less than 3
                {% endif %}
            {% endfor %}
            ''').render(l=[2, 4])
        self.assertEqual(rendered, '''
                less than 3
                4
            ''')

    def test_nested_for_for(self):
        rendered = Template('''
            {% for i in l %}
                {% for j in i %}
                    {{ j }}
                {% endfor %}
            {% endfor %}
            ''').render(l=[[1], [2], [3]])
        self.assertEqual(rendered, '''
                    1
                    2
                    3
            ''')

    def test_index(self):
        rendered = Template("{{ a[2] }}").render(a=[1, 2, 3])
        self.assertEqual(rendered, '3')

    def test_dict_1(self):
        rendered = Template(
            "{{ a['hello'] }}").render(a={'hello': 'flango'})
        self.assertEqual(rendered, 'flango')

    def test_dict_2(self):
        rendered = Template(
            "{{ a.get('hello') }}").render(a={'hello': 'flango'})
        self.assertEqual(rendered, 'flango')

    def test_escape(self):
       rendered = Template("{{ content }}", autoescape=True).render(
           content="<p>hello escape</p>")
       self.assertEqual(rendered, '&lt;p&gt;hello escape&lt;/p&gt;')

    def test_not_escape(self):
       rendered = Template("{{ content }}", autoescape=False).render(
           content="<p>hello escape</p>")
       self.assertEqual(rendered, '<p>hello escape</p>')


class FunctionTest(unittest.TestCase):

    def test_simple_1(self):
        rendered = Template('{{ abs(-3) }}').render()
        self.assertEqual(rendered, '3')

    def test_simple_2(self):
        rendered = Template('{{ len([1, 2, 3]) }}').render()
        self.assertEqual(rendered, '3')

    def test_simple_3(self):
        rendered = Template('{{ [1, 2, 3].index(2) }}').render()
        self.assertEqual(rendered, '1')

    def test_lambda(self):
        rendered = Template(
            '{{ list(map(lambda x: x * 2, [1, 2, 3])) }}').render()
        self.assertEqual(rendered, '[2, 4, 6]')


class SubtemplateTest(unittest.TestCase):

    def test_extends(self):
        rendered = Loader(os.path.dirname(os.path.realpath(__file__))).load(
            'test_extends.html').render(title='flango')
        self.assertEqual(rendered, '''<html>
<title>flango</title>
<head>
    <p>Hello, this is flango.</p>
</head>
<body>
    <p>This block body</p>
</body>
</html>''')

    def test_include(self):
        rendered = Loader(os.path.dirname(os.path.realpath(__file__))).load(
            'test_include.html').render()
        self.assertEqual(rendered, "<p>Included</p>")


if __name__ == '__main__':
    unittest.main()