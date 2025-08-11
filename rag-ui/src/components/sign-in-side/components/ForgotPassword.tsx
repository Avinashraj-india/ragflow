import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import OutlinedInput from '@mui/material/OutlinedInput';

interface ForgotPasswordProps {
  open: boolean;
  handleClose: () => void;
}

const backendURL = import.meta.env.VITE_BACKEND_URL;

export default function ForgotPassword({ open, handleClose }: ForgotPasswordProps) {
  const [step, setStep] = React.useState(1); // 1: email, 2: otp+password
  const [email, setEmail] = React.useState('');
  const [otp, setOtp] = React.useState('');
  const [newPassword, setNewPassword] = React.useState('');
  const [loading, setLoading] = React.useState(false);

  const handleEmailSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);

    try {
      const res = await fetch(`${backendURL}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      if (res.ok) {
        setStep(2);
        alert('OTP sent to your email');
      } else {
        alert('User not found');
      }
    } catch (error) {
      alert('Failed to send OTP');
    }
    setLoading(false);
  };

  const handleResetSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);

    try {
      const res = await fetch(`${backendURL}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp, new_password: newPassword })
      });

      if (res.ok) {
        alert('Password updated successfully');
        handleClose();
        setStep(1);
      } else {
        alert('Invalid OTP or failed to update');
      }
    } catch (error) {
      alert('Failed to reset password');
    }
    setLoading(false);
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      slotProps={{
        paper: {
          component: 'form',
          onSubmit: step === 1 ? handleEmailSubmit : handleResetSubmit,
          sx: { backgroundImage: 'none' },
        },
      }}
    >
      <DialogTitle>{step === 1 ? 'Reset password' : 'Enter OTP & New Password'}</DialogTitle>
      <DialogContent
        sx={{ display: 'flex', flexDirection: 'column', gap: 2, width: '100%' }}
      >
        {step === 1 ? (
          <>
            <DialogContentText>
              Enter your account&apos;s email address, and we&apos;ll send you an OTP to reset your password.
            </DialogContentText>
            <OutlinedInput
              autoFocus
              required
              margin="dense"
              id="email"
              name="email"
              placeholder="Email address"
              type="email"
              fullWidth
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </>
        ) : (
          <>
            <OutlinedInput
              autoFocus
              required
              margin="dense"
              placeholder="Enter 6-digit OTP"
              type="text"
              fullWidth
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
            />
            <OutlinedInput
              required
              margin="dense"
              placeholder="New Password"
              type="password"
              fullWidth
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
          </>
        )}
      </DialogContent>
      <DialogActions sx={{ pb: 3, px: 3 }}>
        <Button onClick={handleClose}>Cancel</Button>
        <Button variant="contained" type="submit" disabled={loading}>
          {loading ? 'Processing...' : step === 1 ? 'Send OTP' : 'Reset Password'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
