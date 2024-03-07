function toggleCheckbox(checkbox) {
  const fillType = checkbox.classList[1];
  const taskId = checkbox.getAttribute('data-task-id')
  console.log(taskId)
  const newFillType =
    fillType === 'empty' ? 'half' : fillType === 'half' ? 'full' : 'empty';

  checkbox.classList.replace(fillType, newFillType);
  const data = {
    status: newFillType.toUpperCase(),
    id: taskId
  };

  fetch(`/api/v1/tasks?id=${taskId}`, {
    method: 'PATCH', // or 'GET' if your endpoint expects a GET request
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data), // convert the JavaScript object to a JSON string
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json(); // or response.text() if your server responds with text
    })
    .then(data => {
      console.log('Success:', data);
      location.reload()
      // Handle success response
    })
    .catch(error => {
      console.error('Error:', error);
      // Handle errors
    });

}


const checkboxes = document.querySelectorAll('.checkbox');

checkboxes.forEach(function (element) {
  element.addEventListener('click', () => {
    toggleCheckbox(element);
  })
});


document.getElementById('title').addEventListener('click', function () {
  window.location.href = '/'; // Assuming the home page is at the root
});


const taskTitles = document.querySelectorAll('.task-title');
taskTitles.forEach(function (element) {
  element.addEventListener('click', () => {
    console.log('test')
    const taskId = element.getAttribute('data-task-id')
    window.location.href = `/${taskId}`;
  })
});