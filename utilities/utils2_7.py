"""
This module contains some utilities methods.
Requires Python 2.7
"""


# To support relative module import
# if __name__ == '__main__':
#     sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from utilities.utils import *

from decorator import decorate


class ArgTypeException(Exception):
    def __init__(self, message):
        if message is None:
            self.message = "ArgTypeException. Please provide correct type"
        else:
            self.message = message
        super(self.__class__, self).__init__(self.message)


# Overrides utils.accepts with a Python 2.6 decorator method for preserving arguments documentation
# http://pythonhosted.org/decorator/documentation.html
def accepts(exception=ArgTypeException, **types):
    """
    http://code.activestate.com/recipes/578809-decorator-to-check-method-param-types/
    Decorator
    Usage :
    @u.accepts(Exception,a=int,b=list,c=(str,unicode))
    def test(a,b=None,c=None)
        print('ok')

    test(13,c=[],b='df')
    >Exception

    Supports string (not in tuple).

    for example
    class Test(object):
        def __init__(self):
            pass
        @u.accepts(Exception,self=object, test='Test')
        def add(self, test):
            return self + test

    NoneType is usable via type(None)
    """
    def _check_accepts(f):
        assert len(types) == f.func_code.co_argcount, \
        'accept number of arguments not equal with function number of arguments in "%s"' % f.func_name
        def new_f(func, *args, **kwds):
            # print("args=" + str(args))
            for i, v in enumerate(args):
                if f.func_code.co_varnames[i] in types:
                    # GuillaumeNM 2016-09-06 Workaround to support str
                    # for not yet defined classes.
                    # FIXME not supported in tuples like (str, int,'MyCustObj')
                    if isinstance(types[f.func_code.co_varnames[i]], str):
                        if types[f.func_code.co_varnames[i]] != v.__class__.__name__:
                            raise exception("arg '%s'=%s does not match %s" % \
                                (f.func_code.co_varnames[i],v.__class__.__name__,types[f.func_code.co_varnames[i]]))
                            del types[f.func_code.co_varnames[i]]
                    # Normal path
                    else:
                        if not isinstance(v, types[f.func_code.co_varnames[i]]):
                            raise exception("arg '%s'=%r does not match %s" % \
                                (f.func_code.co_varnames[i],v,types[f.func_code.co_varnames[i]]))
                            del types[f.func_code.co_varnames[i]]

            for k, v in kwds.iteritems():
                if types.has_key(k) and not isinstance(v, types[k]):
                    raise exception("arg '%s'=%r does not match %s" % \
                        (k,v,types[k]))

            return func(*args, **kwds)
        new_f.func_name = f.func_name
        new_f.__doc__ = f.__doc__
        return decorate(f, new_f)
    return _check_accepts


class Progress(object):
    """
    Dummy class to share an int object across threads
    """
    def __init__(self):
        self.value = 0


def parallel(instance, method_name="", progress=None,
             progressLen=0, *args, **kwargs):
    """
    Generic method to run another method in parallel
    """
    logger.debug('utils2.7::parallel args=%s kwargs = %s'
                 % (args, kwargs))
    logger.debug('Parallel method_name=%s instanceName = %s'
                 % (method_name, instance.name))
    try:
        if method_name =='fingerprinting2':
            getattr(instance, method_name)(force=False, **kwargs)
        else:
            getattr(instance, method_name)(*args, **kwargs)
    except KeyboardInterrupt:
        raise
    except:
        logger.error(
            'Parallel error for method_name=%s instanceName = %s'
            % (method_name, instance.name),
            exc_info=Logger.isDebug())
    else:
        logger.info(
            'Parallel completed successfully for method_name=%s '
            'instanceName = %s'
            % (method_name, instance.name))
    finally:
        try:
            if progressLen != 0:
                # logger.info("progress=%s progressLen=%s" % (progress.value, progressLen))
                progress.value += 1
                # update_progress(float(progress.value) / progressLen,
                #                 text_progress=method_name)
        except:
            logger.error('parallel :: cannot update_progress', exc_info=Logger.isDebug())


def loadConfig(self):
    yaml_config = {}
    conf = ""
    try:
        if self.configFilename and os.path.isfile(self.configFilename):
            conf = self.configFilename
        else:
            conf = self.name + '.conf'
        with open(conf) as config_file:
            yaml_config = yaml.load(config_file.read())
    except:
        logger.error('Configuration file was not loaded properly. %s' %
                     (conf))
    if yaml_config != {}:
        self.config = yaml_config

# Python 2.7+ code.
Application.loadConfig = loadConfig