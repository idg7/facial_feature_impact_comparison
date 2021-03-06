# from average_meter import AverageMeter
# from progress_meter import ProgressMeter
import time
import torch
from tqdm import tqdm
import const
# from const import TRAIN_PHASE, VAL_PHASE
# from metrics import accuracy
# from util import save_checkpoint


class Trainer(object):
    def __init__(self, model, criterion, optimizer, lr_scheduler, model_store, best_acc1:float = 0):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.lr_scheduler = lr_scheduler
        self.model_store = model_store
        self.best_acc1 = best_acc1

    def get_trained_model(self, start_epoch, end_epoch, data_loaders):
        for epoch in range(start_epoch, end_epoch):

            # modelling for one epoch
            self.__per_phase(epoch, const.TRAIN_PHASE)
            phase_loss, phase_acc = self.__per_phase(epoch, const.VAL_PHASE)

            self.lr_scheduler.step()

            # remember best acc@1 and save checkpoint
            is_best = phase_acc > self.best_acc1
            self.best_acc1 = max(phase_acc, self.best_acc1)

            self.model_store.save_model(self.model, self.optimizer, epoch, self.best_acc1, is_best)

    def __per_phase(self, epoch, phase, data_loaders):
        # batch_time, losses, top1, top5, data_time, progress = get_epoch_meters(self.train_loader, epoch)

        if hasattr(data_loaders[phase].sampler, 'indices'):
            phase_size = len(data_loaders[phase].sampler.indices)
        else:
            phase_size = len(data_loaders[phase].dataset)

        phase_loss = 0
        phase_acc = 0

        # switch to modelling mode
        self.model.train(phase == const.TRAIN_PHASE)

        with torch.set_grad_enabled(phase == const.TRAIN_PHASE):
            for i in tqdm(data_loaders[phase], desc=phase):
                images, target = data_loaders[phase][i]

                batch_loss, batch_acc = self.__per_batch(images, target)
                phase_loss += batch_loss / phase_size
                phase_acc += batch_acc / phase_size

        return phase_loss, phase_acc

    def __per_batch(self, images, target):
        if torch.cuda.is_available():
            # TODO: Need to test this modification. before it used to check if GPU is not None. Why?
            images = images.cuda(non_blocking=True)
            target = target.cuda(non_blocking=True)

        # compute output
        output = self.model(images)
        loss = self.criterion(output, target)

        # compute gradient and do optimizer step
        if self.model.training:
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        return loss.data.item(), torch.sum(output == target)