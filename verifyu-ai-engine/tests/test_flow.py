import unittest
from unittest.mock import MagicMock, patch
import base64
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock algosdk if not installed (for Verification in broken env)
try:
    import algosdk
except ImportError:
    print("WARNING: algosdk not found. Mocking it for tests.")
    mock_algosdk = MagicMock()
    sys.modules["algosdk"] = mock_algosdk
    sys.modules["algosdk.v2client"] = MagicMock()
    sys.modules["algosdk.v2client.algod"] = MagicMock()
    sys.modules["algosdk.atomic_transaction_composer"] = MagicMock()
    sys.modules["algosdk.transaction"] = MagicMock()
    sys.modules["algosdk.abi"] = MagicMock()
    sys.modules["algosdk.account"] = MagicMock()
    sys.modules["algosdk.mnemonic"] = MagicMock()

import watcher
import analyzer
import responder
import config

class TestVerifyUAI(unittest.TestCase):

    def test_analyzer_high_absence(self):
        """Test that analyzer returns True for >40% absence"""
        # 50 total, 25 present = 50% attendance = 50% absence (> 40%)
        result = analyzer.analyze_attendance(50, 25)
        self.assertTrue(result)

    def test_analyzer_low_absence(self):
        """Test that analyzer returns False for <40% absence"""
        # 50 total, 40 present = 80% attendance = 20% absence (< 40%)
        result = analyzer.analyze_attendance(50, 40)
        self.assertFalse(result)

    def test_analyzer_boundary(self):
        """Test exact boundary condition"""
        # 40% absence (e.g. 100 total, 60 present)
        # config.ABSENCE_THRESHOLD is 0.40. logic is > 0.40
        result = analyzer.analyze_attendance(100, 60)
        self.assertFalse(result) # 40% is not > 40%
        
        # 41% absence (e.g. 100 total, 59 present)
        result = analyzer.analyze_attendance(100, 59)
        self.assertTrue(result)

    @patch('watcher.algod.AlgodClient')
    def test_watcher_fetch(self, mock_algod_client):
        """Test watcher parsing logic with mocked Algod response"""
        client = mock_algod_client.return_value
        
        # Mock Box Response
        # Box Value: Total(50) + Present(25) = 16 bytes
        total = (50).to_bytes(8, 'big')
        present = (25).to_bytes(8, 'big')
        mock_value_bytes = total + present
        mock_value_b64 = base64.b64encode(mock_value_bytes).decode('utf-8')
        
        client.application_box_by_name.return_value = {'value': mock_value_b64}
        
        data = watcher.fetch_attendance_data(client, 123, "class_101")
        
        self.assertEqual(data['total'], 50)
        self.assertEqual(data['present'], 25)
        self.assertEqual(data['class_id'], "class_101")

    @patch('responder.AtomicTransactionComposer')
    @patch('responder.watcher.get_algod_client')
    @patch('responder.os.getenv')
    @patch('responder.mnemonic.to_private_key')
    @patch('responder.account.address_from_private_key')
    @patch('responder.AccountTransactionSigner')
    def test_responder_trigger(self, mock_signer_cls, mock_addr_from_pk, mock_to_pk, mock_getenv, mock_get_client, mock_atc):
        """Test that responder constructs a transaction"""
        # Mock env var
        mock_getenv.return_value = "shoot island position soft burden budget tooth cruel issue economy destroy investigation collecting brain effort okay end endless aesthetic visual spoil hazard anger ability auction"
        
        # Mock Key Derivation
        mock_to_pk.return_value = "PRIVATE_KEY_BYTES"
        mock_addr_from_pk.return_value = "MOCK_ADDRESS"
        
        # Mock Signer
        mock_signer_instance = mock_signer_cls.return_value
        
        # Mock ATC execute
        instance = mock_atc.return_value
        instance.execute.return_value.tx_ids = ["TXID_123"]
        instance.execute.return_value.confirmed_round = 100
        
        tx_id = responder.trigger_emergency_poll(123, "class_101")
        
        self.assertEqual(tx_id, "TXID_123")
        # Verify add_method_call was called
        self.assertTrue(instance.add_method_call.called)
        
        # Verify arguments
        call_args = instance.add_method_call.call_args
        self.assertEqual(call_args.kwargs['app_id'], 123)
        self.assertIn("class_101", call_args.kwargs['method_args'])

if __name__ == '__main__':
    unittest.main()
