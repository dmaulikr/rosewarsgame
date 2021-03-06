//
//  AIStrategyCatapulter.m
//  WarOfTheRoses
//
//  Created by Heine Skov Kristensen on 2/19/13.
//
//


#import "AIStrategyCatapulter.h"
#import "PathFinderStep.h"

@implementation AIStrategyCatapulter

- (Action *)decideNextActionFromActions:(NSArray *)actions {
    
    Action *action = nil;
    
    NSLog(@"Deciding next action");
    
    for (Action *action in actions) {
        
        PathFinderStep *startPositionStep = action.path[0];
        GridLocation *startPosition =  startPositionStep.location;
                   
        PathFinderStep *endPositionStep = action.path.lastObject;
        GridLocation *endPosition = endPositionStep.location;
        
        if (action.isAttack) {
            action.score += 0.5;
        }
        
        if (action.cardInAction.unitName == kCatapult) {
            action.score += 6;
        }
        
        if (action.cardInAction.unitName == kBallista) {
            action.score += 3;
        }
        
        if (action.cardInAction.unitName == kCatapult && endPosition.row > startPosition.row) {
            action.score += 2;
        }

        if (action.cardInAction.unitName == kBallista && endPosition.row > startPosition.row) {
            action.score += 1;
        }
    }
    
    action = [[actions sortedArrayUsingComparator:^NSComparisonResult(id obj1, id obj2) {
        
        Action *action1 = obj1;
        Action *action2 = obj2;
        
        return action1.score > action2.score;
    }] lastObject];
    
    NSLog(@"Next action found: %@", action);
    
    return action;
}

@end
