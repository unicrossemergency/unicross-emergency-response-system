const formOpenBtn = document.querySelector('#form-open'),
home = document.querySelector('.home'),
formContainer = document.querySelector('.form-container'),
formCloseBtn = document.querySelector('.form-close'),
signupBtn = document.querySelector('#open-signup'),
loginBtn = document.querySelector('#open-login'),
pwshowHideBtn = document.querySelectorAll('.pw-hide');

formOpenBtn.addEventListener('click', () => home.classList.add('show'))
formCloseBtn.addEventListener('click', () => home.classList.remove('show'));

pwshowHideBtn.forEach(icon => {
    icon.addEventListener('click', () => {
    let getPwInput = icon.parentElement.querySelector('input');
    if(getPwInput.type === 'password'){
        getPwInput.type = 'text';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    } else {
        getPwInput.type = 'password';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    }
    });
})
signupBtn.addEventListener('click',(e) => {
    e.preventDefault();
    formContainer.classList.add('active');
});


loginBtn.addEventListener('click',(e) => {
    e.preventDefault();
    formContainer.classList.remove('active');
});