// Birthday Campaign Detail Page JavaScript

const campaignId = window.campaignId || 0;
let campaignData = null;

$(document).ready(function() {
    console.log('Birthday campaign page loaded');
    console.log('Campaign ID:', campaignId);
    
    if (campaignId && campaignId !== '0') {
        loadCampaignDetails();
    } else {
        showError('Invalid campaign ID');
    }
});

async function loadCampaignDetails() {
    try {
        showLoading();
        const response = await fetch(`/api/applications/birthday-campaign/${campaignId}/`);
        const data = await response.json();

        if (response.ok) {
            campaignData = data;
            displayCampaignDetails(campaignData);
            // Load donations separately
            displayDonations(data.donations || []);
        } else {
            throw new Error(data.error || 'Failed to load campaign details');
        }
    } catch (error) {
        console.error('Error loading campaign:', error);
        showError('Failed to load campaign details. The campaign may not exist or may have been removed.');
        // Show empty donations on error
        displayDonations([]);
    }
}

function showLoading() {
    $('#campaign-title').text('Loading...');
    $('#campaign-description').text('Loading campaign details...');
    $('#campaign-organizer span').text('');
    $('#current-amount').text('0');
    $('#target-amount').text('0');
    $('#donors-count').text('0');
    $('#full-description').text('Loading story...');
    $('#target-display').text('0');
    $('#current-display').text('0');
    $('#birthday-date').text('Loading...');
    $('#organizer-name').text('Loading...');
}

function showError(message) {
    $('#campaign-title').text('Campaign Not Found');
    $('#campaign-description').text(message);
    $('#campaign-organizer span').text('');
    $('#current-amount').text('0');
    $('#target-amount').text('0');
    $('#donors-count').text('0');
    $('#full-description').text('This campaign is not available.');
    $('#target-display').text('0');
    $('#current-display').text('0');
    $('#birthday-date').text('N/A');
    $('#organizer-name').text('N/A');
    
    Swal.fire({
        icon: 'error',
        title: 'Campaign Not Found',
        text: message
    });
}

function displayCampaignDetails(campaign) {
    console.log('Displaying campaign details:', campaign);
    
    // Parse numbers properly
    const currentAmount = parseFloat(campaign.current_amount) || 0;
    const targetAmount = parseFloat(campaign.target_amount) || 0;
    const donorsCount = parseInt(campaign.donors_count) || 0;
    
    console.log('Parsed amounts:', { currentAmount, targetAmount, donorsCount });
    
    $('#current-amount').text(currentAmount.toLocaleString());
    $('#target-amount').text(targetAmount.toLocaleString());
    $('#donors-count').text(donorsCount);
    
    // Update additional display elements
    $('#target-display').text(targetAmount.toLocaleString());
    $('#current-display').text(currentAmount.toLocaleString());
    $('#birthday-date').text(new Date(campaign.birthday_date).toLocaleDateString());
    $('#organizer-name').text(campaign.full_name);
    $('#full-description').text(campaign.description);
    
    // Show Pay Now button
    $('#payNowBtn').show();
}

function displayDonations(donations) {
    const container = $('#donations-list');
    container.empty();

    if (!donations || donations.length === 0) {
        container.html('<p class="text-muted">No donations yet. Be the first to donate!</p>');
        return;
    }

    donations.forEach(donation => {
        const donationItem = `
            <div class="donor-item p-3 mb-3 bg-light rounded">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${donation.donor_name}</h6>
                        <p class="mb-1 text-success fw-bold">Rs. ${parseInt(donation.amount).toLocaleString()}</p>
                        ${donation.message ? `<p class="mb-0 text-muted small">"${donation.message}"</p>` : ''}
                    </div>
                    <div class="text-end">
                        <small class="text-muted d-block">${new Date(donation.date).toLocaleDateString()}</small>
                    </div>
                </div>
            </div>
        `;
        container.append(donationItem);
    });
}

function showDonationModal() {
    // Show payment method selection first
    Swal.fire({
        title: 'Choose Payment Method',
        html: `
            <div class="text-center">
                <button class="btn btn-primary btn-lg m-2" onclick="selectPaymentMethod('khalti')">
                    <i class="fas fa-wallet me-2"></i>Khalti
                </button>
                <button class="btn btn-success btn-lg m-2" onclick="selectPaymentMethod('stripe')">
                    <i class="fas fa-credit-card me-2"></i>Stripe
                </button>
            </div>
        `,
        showConfirmButton: false,
        showCancelButton: true,
        cancelButtonText: 'Cancel'
    });
}

function selectPaymentMethod(method) {
    Swal.close();
    if (method === 'khalti') {
        $('#donationModal').modal('show');
    } else {
        Swal.fire({
            icon: 'info',
            title: 'Stripe Payment',
            text: 'Stripe payment integration coming soon!'
        });
    }
}

// Handle donation form submission
$(document).ready(function() {
    $('#donationForm').on('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            donor_name: $('#donor_name').val(),
            amount: $('#amount').val(),
            message: $('#message').val(),
            is_anonymous: $('#is_anonymous').is(':checked')
        };
        
        if (!formData.donor_name || !formData.amount || formData.amount < 100) {
            Swal.fire({
                icon: 'warning',
                title: 'Invalid Input',
                text: 'Please fill all required fields and ensure minimum donation is Rs. 100'
            });
            return;
        }
        
        // Create donation record directly (simplified for now)
        createDonationRecord(formData);
    });
});

async function createDonationRecord(donationData) {
    try {
        Swal.fire({
            title: 'Processing Donation...',
            text: 'Please wait while we record your donation.',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch(`/api/applications/birthday-campaign/${campaignId}/donate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(donationData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            Swal.fire({
                icon: 'success',
                title: 'Thank You!',
                text: 'Your donation has been recorded successfully!'
            }).then(() => {
                // Close modal and refresh campaign data
                $('#donationModal').modal('hide');
                $('#donationForm')[0].reset();
                loadCampaignDetails();
            });
        } else {
            throw new Error(result.error || 'Failed to record donation');
        }
    } catch (error) {
        console.error('Donation error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Donation Failed',
            text: error.message || 'Failed to record donation. Please try again.'
        });
    }
}

async function makeDonation() {
    // Check if user is logged in
    if (!window.djangoUser || !window.djangoUser.isAuthenticated) {
        // Show login modal instead
        const loginModal = document.getElementById('loginModal');
        if (loginModal) {
            loginModal.style.display = 'flex';
            document.body.classList.add('modal-open');
            return;
        } else {
            Swal.fire({
                icon: 'warning',
                title: 'Login Required',
                text: 'Please login to make a donation.',
                showCancelButton: true,
                confirmButtonText: 'Login',
                cancelButtonText: 'Cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = '/accounts/login/';
                }
            });
            return;
        }
    }

    const form = document.getElementById('donationForm');
    const formData = new FormData(form);

    if (!formData.get('amount') || formData.get('amount') < 100) {
        Swal.fire({
            icon: 'warning',
            title: 'Invalid Amount',
            text: 'Minimum donation amount is Rs. 100'
        });
        return;
    }

    try {
        // Show loading
        Swal.fire({
            title: 'Processing Donation...',
            text: 'Please wait while we prepare your payment.',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        // Initiate Khalti payment
        const response = await fetch(`/api/applications/birthday-campaign/${campaignId}/donate/`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success && data.payment_url) {
            window.location.href = data.payment_url;
        } else {
            throw new Error(data.error || 'Failed to initiate donation');
        }
    } catch (error) {
        console.error('Donation error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Donation Failed',
            text: error.message || 'Failed to process donation. Please try again.'
        });
    }
}

// Print donation receipt
function printReceipt(donorName, amount, date, message) {
    const receiptWindow = window.open('', '_blank', 'width=600,height=800');
    const receiptContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Donation Receipt - Aarambha Foundation</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    line-height: 1.6;
                    color: #333;
                }
                .header { 
                    text-align: center; 
                    border-bottom: 2px solid #333; 
                    padding-bottom: 20px; 
                    margin-bottom: 30px; 
                }
                .logo { 
                    font-size: 28px; 
                    font-weight: bold; 
                    color: #2c3e50;
                    margin-bottom: 5px;
                }
                .subtitle { 
                    color: #7f8c8d; 
                    font-size: 14px;
                }
                .receipt-info { 
                    margin: 20px 0; 
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                }
                .info-row {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                    padding: 5px 0;
                    border-bottom: 1px dotted #ddd;
                }
                .info-row:last-child {
                    border-bottom: none;
                }
                .label { 
                    font-weight: bold; 
                    color: #2c3e50;
                }
                .amount { 
                    font-size: 24px; 
                    font-weight: bold; 
                    color: #27ae60;
                    text-align: center;
                    padding: 15px;
                    background: #e8f5e8;
                    border-radius: 8px;
                    margin: 20px 0;
                }
                .footer { 
                    margin-top: 40px; 
                    text-align: center; 
                    font-size: 12px; 
                    color: #666;
                    border-top: 1px solid #ddd;
                    padding-top: 20px;
                }
                .thank-you {
                    font-size: 18px;
                    color: #2c3e50;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .print-btn {
                    padding: 12px 24px;
                    background: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                    margin-top: 20px;
                }
                .print-btn:hover {
                    background: #2980b9;
                }
                @media print { 
                    .no-print { display: none; }
                    body { margin: 0; }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">🎂 Aarambha Foundation</div>
                <div class="subtitle">Transforming Lives Through Education</div>
                <h2 style="margin-top: 20px; color: #e74c3c;">🧾 Donation Receipt</h2>
            </div>
            
            <div class="receipt-info">
                <div class="info-row">
                    <span class="label">Campaign:</span>
                    <span>${campaignData ? campaignData.title : 'Birthday Campaign'}</span>
                </div>
                <div class="info-row">
                    <span class="label">Campaign Organizer:</span>
                    <span>${campaignData ? campaignData.full_name : 'N/A'}</span>
                </div>
                <div class="info-row">
                    <span class="label">Donor Name:</span>
                    <span>${donorName}</span>
                </div>
                <div class="info-row">
                    <span class="label">Donation Date:</span>
                    <span>${new Date(date).toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                    })}</span>
                </div>
                ${message ? `
                <div class="info-row">
                    <span class="label">Message:</span>
                    <span>"${message}"</span>
                </div>
                ` : ''}
                <div class="info-row">
                    <span class="label">Receipt Generated:</span>
                    <span>${new Date().toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                    })}</span>
                </div>
            </div>
            
            <div class="amount">
                💰 Donation Amount: Rs. ${parseInt(amount).toLocaleString()}
            </div>
            
            <div class="footer">
                <div class="thank-you">🙏 Thank you for your generous donation!</div>
                <p>Your contribution helps us provide quality education to underprivileged children.</p>
                <p>This receipt serves as proof of your donation for tax purposes.</p>
                <p><strong>Contact:</strong> info@aarambhafoundation.org | Phone: +977-1-XXXXXXX</p>
                <p><strong>Address:</strong> Kathmandu, Nepal</p>
                <button class="no-print print-btn" onclick="window.print()">🖨️ Print Receipt</button>
            </div>
        </body>
        </html>
    `;
    
    receiptWindow.document.write(receiptContent);
    receiptWindow.document.close();
    receiptWindow.focus();
}
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Test function to manually verify payment with pidx from URL
function testVerification() {
    const urlParams = new URLSearchParams(window.location.search);
    let pidx = urlParams.get('pidx');
    
    if (!pidx) {
        // For testing with your specific pidx
        Swal.fire({
            title: 'Test Payment Verification',
            html: `
                <p>Enter the pidx from your Khalti payment:</p>
                <input type="text" id="test-pidx" class="swal2-input" placeholder="Enter pidx" value="iwNEAiLGHAhso6kPoGVcB8">
            `,
            showCancelButton: true,
            confirmButtonText: 'Verify Payment',
            preConfirm: () => {
                const testPidx = document.getElementById('test-pidx').value;
                if (!testPidx) {
                    Swal.showValidationMessage('Please enter a pidx');
                    return false;
                }
                return testPidx;
            }
        }).then((result) => {
            if (result.isConfirmed) {
                console.log('Testing verification with pidx:', result.value);
                verifyPayment(result.value);
            }
        });
        return;
    }
    
    console.log('Testing verification with pidx:', pidx);
    verifyPayment(pidx);
}

// Simulate a successful payment for testing
function simulatePaymentSuccess() {
    Swal.fire({
        title: 'Simulating Payment...',
        text: 'This will refresh the campaign data to show updated amounts.',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    // Reload campaign data after a short delay
    setTimeout(async () => {
        await loadCampaignDetails();
        Swal.fire({
            icon: 'success',
            title: 'Test Complete!',
            text: 'Campaign data has been refreshed. Check if the amounts updated.'
        });
    }, 1500);
}