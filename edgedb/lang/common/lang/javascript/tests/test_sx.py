##
# Copyright (c) 2012 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


from .base import JSFunctionalTest


class TestJSsx(JSFunctionalTest):
    def test_utils_lang_js_sx_is(self):
        '''JS
        // %from semantix.utils.lang.javascript import sx

        assert.ok(sx.is_string('aaa'));
        assert.ok(sx.is_string(''));
        assert.not(sx.is_string(123));
        assert.not(sx.is_string(null));
        assert.not(sx.is_string(void(0)));
        assert.not(sx.is_string({}));

        assert.ok(sx.is_array([]));
        assert.ok(sx.is_array([1,2]));
        assert.not(sx.is_array(123));
        assert.not(sx.is_array({}));
        assert.not(sx.is_array(''));
        assert.not(sx.is_array(void(0)));

        assert.ok(sx.is_object({}));
        assert.ok(sx.is_object(new (function(){})));
        assert.not(sx.is_object(123));
        assert.not(sx.is_object([]));
        assert.not(sx.is_object(null));
        assert.not(sx.is_object(''));
        assert.not(sx.is_object(void(0)));
        '''

    def test_utils_lang_js_sx_error(self):
        '''JS
        // %from semantix.utils.lang.javascript import sx

        assert.equal(String(new sx.Error('foo')), 'sx.Error: foo');
        assert.equal(String(sx.Error), 'sx.Error');
        '''

    def test_utils_lang_js_sx_hasattr(self):
        '''JS
        // %from semantix.utils.lang.javascript import sx

        assert.ok(sx.hasattr({'a': 'b'}, 'a'));
        assert.not(sx.hasattr({}, 'hasOwnProperty'));

        // ----

        var foo = function() {};
        foo.prototype = {
            'a': 'b',
            'hasOwnProperty': function() {
                return true;
            }
        };
        foo = new foo();
        foo.b = 'c';

        assert.ok(sx.hasattr(foo, 'b'));
        assert.ok(sx.hasattr(foo, 'a', true)); // weak

        assert.not(sx.hasattr(foo, 'a'));
        assert.not(sx.hasattr(foo, 'hasOwnProperty'));
        assert.not(sx.hasattr(foo, 'c', true)); // weak

        assert.not(sx.hasattr(null, 'a'));
        assert.not(sx.hasattr(void(0), 'a'));
        '''

    def test_utils_lang_js_sx_first(self):
        '''JS
        // %from semantix.utils.lang.javascript import sx

        assert.ok(sx.first([1, 2, 3]) === 1);
        assert.ok(sx.first({'a': 'b', 'c': 'd'}) === 'b');
        assert.ok(sx.first('xyz') === 'x');

        assert.ok(sx.first([], 42) === 42);
        assert.ok(sx.first({}, 42) === 42);
        assert.ok(sx.first('', 42) === 42);

        assert.raises(function() {
            sx.first(1);
        }, {error: sx.Error,
            error_re: 'supports only arrays and objects'});

        assert.raises(function() {
            sx.first({});
        }, {error: sx.Error,
            error_re: 'empty object passed with no default'});

        assert.raises(function() {
            sx.first([]);
        }, {error: sx.Error,
            error_re: 'empty array passed with no default'});

        assert.raises(function() {
            sx.first('');
        }, {error: sx.Error,
            error_re: 'empty string passed with no default'});
        '''

    def test_utils_lang_js_sx_len(self):
        '''JS
        // %from semantix.utils.lang.javascript import sx

        assert.equal(sx.len([]), 0);
        assert.equal(sx.len([1]), 1);
        assert.equal(sx.len([2, []]), 2);

        assert.equal(sx.len({}), 0);
        assert.equal(sx.len({'1': '2'}), 1);

        var foo = function() {};
        foo.prototype = {'a': 'b'};
        foo = new foo();
        foo.b = 'c';
        assert.equal(sx.len(foo), 1);

        assert.raises(function() {
            sx.len(1);
        }, {
            error: sx.Error,
            error_re: 'supports only objects and arrays'
        });

        assert.equal(sx.len(''), 0);
        assert.equal(sx.len('123'), 3);
        '''

    def test_utils_lang_js_sx_each(self):
        '''JS
        // %from semantix.utils.lang.javascript import sx

        assert.equal(
            (function() {
                var cnt = 0;
                sx.each([], function(value, idx) {
                    cnt += idx * value;
                });
                return cnt;
            })(),

            0
        );

        assert.equal(
            (function() {
                var cnt = 0;
                sx.each([10, 20, 30], function(value, idx) {
                    cnt += idx * value;
                });
                return cnt;
            })(),

            80
        );

        assert.equal(
            (function() {
                var cnt = 0;
                sx.each([10, 20, 30], function(value) {
                    cnt += value;
                });
                return cnt;
            })(),

            60
        );

        assert.equal(
            (function() {
                var cnt = 0;
                sx.each([10, 20, 30], function(value, idx, desc) {
                    cnt += idx * value;

                    if (value === 10 && idx === 0 && desc.first) {
                        cnt += 100;
                    }
                    else if (value === 30 && idx === 2 && desc.last) {
                        cnt += 1000;
                    } else {
                        if (desc.first) {
                            cnt += 0.1;
                        }

                        if (desc.last) {
                            cnt += 0.2;
                        }
                    }
                });
                return cnt;
            })(),

            1180
        );

        assert.equal(
            (function() {
                var cnt = 0;
                sx.each({'1': 10, '2': 20, '3': 30}, function(value, idx) {
                    cnt += parseInt(idx) * value;
                });
                return cnt;
            })(),

            140
        );

        assert.equal(
            (function() {
                var cnt = 0;
                sx.each({'1': 10, '2': 20, '3': 30}, function(value) {
                    cnt += value;
                });
                return cnt;
            })(),

            60
        );

        assert.equal(
            (function() {
                var cnt = 0;
                sx.each({}, function(value) {
                    cnt += value;
                });
                return cnt;
            })(),

            0
        );

        assert.equal(
            (function() {
                var cnt = 0;
                sx.each({'1': 10, '2': 20, '3': 30}, function(value, idx, desc) {
                    cnt += parseInt(idx) * value;

                    if (value === 10 && idx === '1' && desc.first) {
                        cnt += 100;
                    }
                    else if (value === 30 && idx === '3' && desc.last) {
                        cnt += 1000;
                    } else {
                        if (desc.first) {
                            cnt += 0.1;
                        }

                        if (desc.last) {
                            cnt += 0.2;
                        }
                    }
                });
                return cnt;
            })(),

            1240
        );
        '''

    def test_utils_lang_js_sx_str(self):
        '''JS
        // %from semantix.utils.lang.javascript import sx

        assert.equal(sx.str.trim('aaa'), 'aaa');
        assert.equal(sx.str.trim('a a  a'), 'a a  a');
        assert.equal(sx.str.trim('  a a  a'), 'a a  a');
        assert.equal(sx.str.trim('a a  a   '), 'a a  a');
        assert.equal(sx.str.trim(   'a a  a   '), 'a a  a');

        assert.ok(sx.str.endswith('aaa', 'a'));
        assert.ok(sx.str.endswith('a', 'a'));
        assert.ok(sx.str.endswith('abc', 'bc'));
        assert.ok(sx.str.endswith('abc', ''));
        assert.ok(sx.str.endswith('', ''));
        assert.not(sx.str.endswith('1abcbc', 'abc'));
        assert.not(sx.str.endswith('abc', 'b'));
        assert.not(sx.str.endswith('', 'b'));

        assert.ok(sx.str.startswith('aaa', 'a'));
        assert.ok(sx.str.startswith('a', 'a'));
        assert.ok(sx.str.startswith('abc', 'ab'));
        assert.ok(sx.str.startswith('abc', ''));
        assert.ok(sx.str.startswith('', ''));
        assert.not(sx.str.startswith('abc', 'b'));
        assert.not(sx.str.startswith('', 'b'));
        '''