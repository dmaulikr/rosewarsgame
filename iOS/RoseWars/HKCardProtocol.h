//
//  HKCardProtocol.h
//  RoseWars
//
//  Created by Heine Kristensen on 08/02/15.
//  Copyright (c) 2015 Heine Skov Kristensen. All rights reserved.
//

#import <Foundation/Foundation.h>

@class GameManager;
@protocol HKCardProtocol <NSObject>

@property (nonatomic, strong) GameManager *gamemanager;
@property (nonatomic, assign) CardColors cardColor;

@end
