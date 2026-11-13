import { feederService } from './feeder.service.js';

feederService.start();

process.on('SIGINT', () => {
  feederService.stop();
  process.exit(0);
});

process.on('SIGTERM', () => {
  feederService.stop();
  process.exit(0);
});
