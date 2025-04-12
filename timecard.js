// Timecard Application JavaScript

$(document).ready(function() {
    // Initialize the application
    updateDateTime();
    setInterval(updateDateTime, 1000);
    loadEmployees();
    
    // Button event listeners
    $('#clock-in-btn').on('click', handleClockIn);
    $('#break-start-btn').on('click', handleBreakStart);
    $('#break-end-btn').on('click', handleBreakEnd);
    $('#clock-out-btn').on('click', handleClockOut);
    
    // Employee selection change
    $('#employee-select').on('change', handleEmployeeChange);
    
    // New employee form submission
    $('#new-employee-form').on('submit', handleNewEmployee);
});

// Update the current date and time display
function updateDateTime() {
    const now = new Date();
    
    // Format time: HH:MM:SS
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const timeString = `${hours}:${minutes}:${seconds}`;
    
    // Format date: Day, Month Date, Year
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dateString = now.toLocaleDateString('en-US', options);
    
    $('#current-time').text(timeString);
    $('#current-date').text(dateString);
}

// Load employees from the server
function loadEmployees() {
    // This will be replaced with actual API call in the backend implementation
    // For now, we'll use mock data
    const mockEmployees = [
        { id: 1, name: 'John Doe' },
        { id: 2, name: 'Jane Smith' },
        { id: 3, name: 'Bob Johnson' }
    ];
    
    const select = $('#employee-select');
    select.empty();
    select.append('<option value="" selected disabled>Choose employee...</option>');
    
    mockEmployees.forEach(employee => {
        select.append(`<option value="${employee.id}">${employee.name}</option>`);
    });
}

// Handle employee selection change
function handleEmployeeChange() {
    const employeeId = $(this).val();
    
    if (employeeId) {
        // Enable/disable buttons based on current status
        // This will be replaced with actual API call in the backend implementation
        // For now, we'll assume the employee is not clocked in
        updateButtonStates('off');
        
        // Update status display
        $('#status-message').text('Not clocked in');
        $('#status-display').removeClass('status-working status-break').addClass('status-off');
        
        // Load today's activity for the selected employee
        loadEmployeeActivity(employeeId);
    } else {
        // Disable all buttons if no employee is selected
        disableAllButtons();
        $('#status-message').text('Please select an employee to begin');
        $('#status-display').removeClass('status-working status-break status-off').addClass('alert-info');
        $('#activity-log').empty();
    }
}

// Load employee activity for today
function loadEmployeeActivity(employeeId) {
    // This will be replaced with actual API call in the backend implementation
    // For now, we'll use mock data
    const mockActivity = [
        { type: 'clock-in', time: '08:00:00', description: 'Clocked in' },
        { type: 'break-start', time: '10:15:00', description: 'Started break' },
        { type: 'break-end', time: '10:30:00', description: 'Ended break' }
    ];
    
    const activityLog = $('#activity-log');
    activityLog.empty();
    
    if (mockActivity.length === 0) {
        activityLog.append('<li class="list-group-item">No activity recorded today</li>');
        return;
    }
    
    mockActivity.forEach(activity => {
        const activityItem = `
            <li class="list-group-item activity-item activity-${activity.type}">
                <span class="activity-time">${activity.time}</span>
                <span class="activity-description"> - ${activity.description}</span>
            </li>
        `;
        activityLog.append(activityItem);
    });
}

// Handle clock in button click
function handleClockIn() {
    const employeeId = $('#employee-select').val();
    
    if (!employeeId) return;
    
    // This will be replaced with actual API call in the backend implementation
    // For now, we'll just update the UI
    
    // Update button states
    updateButtonStates('working');
    
    // Update status display
    $('#status-message').text('Currently working');
    $('#status-display').removeClass('status-off status-break').addClass('status-working highlight');
    
    // Add activity to log
    const now = new Date();
    const timeString = now.toTimeString().split(' ')[0];
    const activityItem = `
        <li class="list-group-item activity-item activity-clock-in">
            <span class="activity-time">${timeString}</span>
            <span class="activity-description"> - Clocked in</span>
        </li>
    `;
    $('#activity-log').prepend(activityItem);
    
    // Show success message
    showAlert('success', 'Successfully clocked in!');
}

// Handle start break button click
function handleBreakStart() {
    const employeeId = $('#employee-select').val();
    
    if (!employeeId) return;
    
    // This will be replaced with actual API call in the backend implementation
    // For now, we'll just update the UI
    
    // Update button states
    updateButtonStates('break');
    
    // Update status display
    $('#status-message').text('On break');
    $('#status-display').removeClass('status-working status-off').addClass('status-break highlight');
    
    // Add activity to log
    const now = new Date();
    const timeString = now.toTimeString().split(' ')[0];
    const activityItem = `
        <li class="list-group-item activity-item activity-break-start">
            <span class="activity-time">${timeString}</span>
            <span class="activity-description"> - Started break</span>
        </li>
    `;
    $('#activity-log').prepend(activityItem);
    
    // Show success message
    showAlert('success', 'Break started!');
}

// Handle end break button click
function handleBreakEnd() {
    const employeeId = $('#employee-select').val();
    
    if (!employeeId) return;
    
    // This will be replaced with actual API call in the backend implementation
    // For now, we'll just update the UI
    
    // Update button states
    updateButtonStates('working');
    
    // Update status display
    $('#status-message').text('Currently working');
    $('#status-display').removeClass('status-break status-off').addClass('status-working highlight');
    
    // Add activity to log
    const now = new Date();
    const timeString = now.toTimeString().split(' ')[0];
    const activityItem = `
        <li class="list-group-item activity-item activity-break-end">
            <span class="activity-time">${timeString}</span>
            <span class="activity-description"> - Ended break</span>
        </li>
    `;
    $('#activity-log').prepend(activityItem);
    
    // Show success message
    showAlert('success', 'Break ended!');
}

// Handle clock out button click
function handleClockOut() {
    const employeeId = $('#employee-select').val();
    
    if (!employeeId) return;
    
    // This will be replaced with actual API call in the backend implementation
    // For now, we'll just update the UI
    
    // Update button states
    updateButtonStates('off');
    
    // Update status display
    $('#status-message').text('Clocked out');
    $('#status-display').removeClass('status-working status-break').addClass('status-off highlight');
    
    // Add activity to log
    const now = new Date();
    const timeString = now.toTimeString().split(' ')[0];
    const activityItem = `
        <li class="list-group-item activity-item activity-clock-out">
            <span class="activity-time">${timeString}</span>
            <span class="activity-description"> - Clocked out</span>
        </li>
    `;
    $('#activity-log').prepend(activityItem);
    
    // Show success message
    showAlert('success', 'Successfully clocked out!');
}

// Handle new employee form submission
function handleNewEmployee(e) {
    e.preventDefault();
    
    const name = $('#employee-name').val().trim();
    const email = $('#employee-email').val().trim();
    
    if (!name || !email) {
        showAlert('danger', 'Please fill in all fields');
        return;
    }
    
    // This will be replaced with actual API call in the backend implementation
    // For now, we'll just show a success message and reset the form
    
    showAlert('success', `New employee "${name}" added successfully!`);
    
    // Reset form
    $('#employee-name').val('');
    $('#employee-email').val('');
    
    // Reload employees (in real implementation, this would fetch from server)
    setTimeout(loadEmployees, 1000);
}

// Update button states based on current status
function updateButtonStates(status) {
    switch (status) {
        case 'off':
            // Not clocked in
            $('#clock-in-btn').prop('disabled', false);
            $('#break-start-btn').prop('disabled', true);
            $('#break-end-btn').prop('disabled', true);
            $('#clock-out-btn').prop('disabled', true);
            break;
        case 'working':
            // Clocked in and working
            $('#clock-in-btn').prop('disabled', true);
            $('#break-start-btn').prop('disabled', false);
            $('#break-end-btn').prop('disabled', true);
            $('#clock-out-btn').prop('disabled', false);
            break;
        case 'break':
            // On break
            $('#clock-in-btn').prop('disabled', true);
            $('#break-start-btn').prop('disabled', true);
            $('#break-end-btn').prop('disabled', false);
            $('#clock-out-btn').prop('disabled', false);
            break;
        default:
            disableAllButtons();
    }
}

// Disable all buttons
function disableAllButtons() {
    $('#clock-in-btn').prop('disabled', true);
    $('#break-start-btn').prop('disabled', true);
    $('#break-end-btn').prop('disabled', true);
    $('#clock-out-btn').prop('disabled', true);
}

// Show alert message
function showAlert(type, message) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Insert alert before the first card
    $('.card:first').before(alertHtml);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        $('.alert').alert('close');
    }, 3000);
}
