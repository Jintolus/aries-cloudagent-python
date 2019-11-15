import pytest
from asynctest import (
    mock as async_mock,
    TestCase as AsyncTestCase,
)

from ......messaging.request_context import RequestContext
from ......messaging.message_delivery import MessageDelivery
from ......messaging.responder import MockResponder

from ...messages.credential_proposal import CredentialProposal
from .. import credential_proposal_handler as handler


class TestCredentialProposalHandler(AsyncTestCase):
    async def test_called(self):
        request_context = RequestContext()
        request_context.message_delivery = MessageDelivery()

        with async_mock.patch.object(
            handler, "CredentialManager", autospec=True
        ) as mock_cred_mgr:
            mock_cred_mgr.return_value.receive_proposal = async_mock.CoroutineMock(
                return_value=async_mock.MagicMock()
            )
            mock_cred_mgr.return_value.receive_proposal.return_value.auto_offer = False
            request_context.message = CredentialProposal()
            request_context.connection_ready = True
            handler_inst = handler.CredentialProposalHandler()
            responder = MockResponder()
            await handler_inst.handle(request_context, responder)

        mock_cred_mgr.assert_called_once_with(request_context)
        mock_cred_mgr.return_value.receive_proposal.assert_called_once_with()
        assert not responder.messages

    async def test_called_auto_offer(self):
        request_context = RequestContext()
        request_context.message_delivery = MessageDelivery()
        request_context.connection_record = async_mock.MagicMock()

        with async_mock.patch.object(
            handler, "CredentialManager", autospec=True
        ) as mock_cred_mgr:
            mock_cred_mgr.return_value.receive_proposal = async_mock.CoroutineMock(
                return_value=async_mock.MagicMock()
            )
            mock_cred_mgr.return_value.receive_proposal.return_value.auto_offer = True
            mock_cred_mgr.return_value.create_offer = async_mock.CoroutineMock(
                return_value=(None, "credential_offer_message")
            )
            request_context.message = CredentialProposal()
            request_context.connection_ready = True
            handler_inst = handler.CredentialProposalHandler()
            responder = MockResponder()
            await handler_inst.handle(request_context, responder)

        mock_cred_mgr.assert_called_once_with(request_context)
        mock_cred_mgr.return_value.receive_proposal.assert_called_once_with()
        messages = responder.messages
        assert len(messages) == 1
        (result, target) = messages[0]
        assert result == "credential_offer_message"
        assert target == {}

    async def test_called_not_ready(self):
        request_context = RequestContext()
        request_context.message_delivery = MessageDelivery()

        with async_mock.patch.object(
            handler, "CredentialManager", autospec=True
        ) as mock_cred_mgr:
            mock_cred_mgr.return_value.receive_proposal = (
                async_mock.CoroutineMock()
            )
            request_context.message = CredentialProposal()
            request_context.connection_ready = False
            handler_inst = handler.CredentialProposalHandler()
            responder = MockResponder()
            with self.assertRaises(handler.HandlerException):
                await handler_inst.handle(request_context, responder)

        assert not responder.messages
