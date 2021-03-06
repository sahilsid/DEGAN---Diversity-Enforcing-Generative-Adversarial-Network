"""
Purpose: Evaluate the results of the 1D GMM experiment using the .pth file
Author: Vineet Madan
Date: 6 July 2019
"""

import argparse, os
import torch
from calculations import calculate_KL_divergence
from GMMDiscriminator import GMMDiscriminator
from GMMSharedGenerator import GMMSharedGenerator
from GMMUnsharedGenerator import GMMUnsharedGenerator
import matplotlib.pyplot as plt
from utils import plot_loss_graph, generate_noise_for_generator, calculate_KL_divergence

from Logger import Logger
import random
import numpy as np



torch.set_printoptions(precision=10)

parser = argparse.ArgumentParser()

parser.add_argument('--folder', help='directory name of the experiment', type=str)
parser.add_argument('--gpu', help='1 if run on gpu and 0 otherwise', type=int)
parser.add_argument('--gpu_add', help='address of the gpu', type=int)
parser.add_argument('--epoch', help='suffix of the .pth file')


args = parser.parse_args()
print(args)
folder = args.folder

logger = Logger(folder+'/eval_log.txt', mode='a')

device = torch.device("cuda:"+str(args.gpu_add) if (torch.cuda.is_available() and args.gpu > 0) else "cpu")
print("DEVICE is {}".format(device))


"""
Retrieve everything stored in the pth file
"""
#################################

for checkpoint_num in range(50):
	checkpoint = torch.load(folder+'/model_save'+str(checkpoint_num)+'.pth')

	G_losses = checkpoint['g_losses']
	D_losses = checkpoint['d_losses']
	train_data = checkpoint['train_data']#this is the real dataset
	g_state_dict = checkpoint['g_state_dict']
	optim_g_state_dict= checkpoint['optim_g_state_dict']
	args = checkpoint['args']
	curr_epoch = checkpoint['epoch']

	manualSeed = args.seed
	print("Random Seed: ", manualSeed)
	random.seed(manualSeed)
	torch.manual_seed(manualSeed)

	torch.backends.cudnn.deterministic = True
	torch.backends.cudnn.benchmark = False

	np.random.seed(manualSeed)


	###################################



	#Plot the loss graph and save to file
	plot_loss_graph(folder, 'G-Loss',G_losses)
	plot_loss_graph(folder, 'D-Loss', D_losses)

	#create the logger


	if args.sharing==1:
	    generator = GMMSharedGenerator(args.n_z)
	    
	else:
	    generator = GMMUnsharedGenerator(args.n_z)


	#load the weights for the generator model
	generator.load_state_dict(g_state_dict)
	generator.to(device)
	generator.eval()

	test_noise = generate_noise_for_generator(train_data.size(0)//args.num_generators, args.n_z, device)
	test_result = generator(test_noise).detach()

	KL_divergence = calculate_KL_divergence(train_data, test_result.detach(), min_obs=0, max_obs=130, bin_size=0.1)

	logger.log("\n-------------------------------------------------\n")
	logger.log("For Epoch: {} KL Divergence is {}".format(checkpoint_num, KL_divergence))