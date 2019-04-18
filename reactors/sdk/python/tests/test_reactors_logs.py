from reactors.utils import Reactor
import pytest
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)
sys.path.append('/reactors')


def test_read_logtoken_config():
    '''Read the API token for log aggregation from config.yml'''
    r = Reactor()
    assert 'token' in r.settings.logs


def test_read_logtoken_env(monkeypatch):
    '''Read the API token for log aggregation from environment'''
    monkeypatch.setenv('_REACTOR_LOGS_TOKEN', 'VewyVewySekwit')
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'DEBUG')
    r = Reactor()
    assert r.settings.logs.token == 'VewyVewySekwit'

@pytest.mark.skipif(sys.version_info.major >= 3,
                    reason="Test itself is not yet Py3 compatible")
def test_log_stderr(caplog, capsys):
    '''Verify logging to stderr works'''
    message = 'Hello'
    r = Reactor()
    r.logger.info(message)
    out, err = capsys.readouterr()
    assert [message] == [rec.message for rec in caplog.records]
    assert message in err
    assert message not in out


# def test_logger_logfile(monkeypatch):
#     '''Verify that message is written to a file'''
#     monkeypatch.setenv('_REACTOR_LOGS_FILE', 'testing.log')
#     monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'DEBUG')
#     message = 'Hola'
#     r = Reactor()
#     r.logger.info(message)
#     file = open('testing.log', 'r')
#     assert message in file.read()
#     os.remove('testing.log')

@pytest.mark.skipif(sys.version_info.major >= 3,
                    reason="Test itself is not yet Py3 compatible")
def test_log_redact_env(caplog, capsys, monkeypatch):
    '''Verify that the text of an override value cannot be logged'''
    monkeypatch.setenv('_REACTOR_REDACT', 'VewyVewySekwit')
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'DEBUG')
    r = Reactor()
    r.logger.debug(r.settings)
    out, err = capsys.readouterr()
    assert 'VewyVewySekwit' in caplog.text
    assert 'VewyVewySekwit' not in err
    assert 'VewyVewySekwit' not in out


@pytest.mark.skipif(sys.version_info.major >= 3,
                    reason="Test itself is not yet Py3 compatible")
def test_log_redact_nonce(caplog, capsys, monkeypatch):
    '''Verify that x-nonce is redacted since it is an impersonation token'''
    message = 'VewyVewySekwit'
    monkeypatch.setenv('x-nonce', message)
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'DEBUG')
    r = Reactor()
    r.logger.debug('context: {}'.format(r.context))
    out, err = capsys.readouterr()
    assert message not in err
    assert message in caplog.text


@pytest.mark.skipif(sys.version_info.major >= 3,
                    reason="Test itself is not yet Py3 compatible")
def test_log_redact_apitoken(caplog, capsys, monkeypatch):
    '''Verify that x-nonce is redacted since it is an impersonation token'''
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'DEBUG')
    r = Reactor()
    message = r._token
    r.logger.debug('redact this token: {}'.format(message))
    out, err = capsys.readouterr()
    assert message not in err
    assert message in caplog.text


@pytest.mark.skipif(sys.version_info.major >= 3,
                    reason="Test itself is not yet Py3 compatible")
def test_log_redact_inited(caplog, capsys, monkeypatch):
    '''Verify that content of 'redactions' list passed to init() are honored'''
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'DEBUG')
    message = 'Sekwit'
    r = Reactor(redactions=[message])
    r.logger.debug('I have a Very{}Message for you!'.format(message))
    out, err = capsys.readouterr()
    assert message not in err
    assert message in caplog.text
