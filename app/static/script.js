function toggleCheckbox(checkbox) {
  const fillType = checkbox.classList[1];
  const taskId = checkbox.id
  const newFillType =
    fillType === 'empty' ? 'half' : fillType === 'half' ? 'full' : 'empty';

  checkbox.classList.replace(fillType, newFillType);
  console.log(taskId)
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


const elements = document.querySelectorAll('.checkbox');

elements.forEach(function (element) {
  element.addEventListener('click', () => {
    toggleCheckbox(element);
  })
});
