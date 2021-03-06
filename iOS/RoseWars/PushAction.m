//
//  PushAction.m
//  WarOfTheRoses
//
//  Created by Heine Skov Kristensen on 4/5/13.
//
//

#import "PushAction.h"
#import "PathFinderStep.h"

@implementation PushAction

@synthesize actionType = _actionType;
@synthesize startLocation = _startLocation;
@synthesize battleReport = _battleReport;

- (id)initWithGameManager:(GameManager*)gamemanager path:(NSArray *)path andCardInAction:(Card *)card {
    
    self = [super initWithGameManager:gamemanager path:path andCardInAction:card enemyCard:nil];
    
    if (self) {
        _actionType = kActionTypePush;
        _startLocation = card.cardLocation;
    }
    
    return self;
}

- (BOOL)isAttack {
    
    return NO;
}

- (BOOL)isMove {
    
    return YES;
}

- (ActionTypes)actionType {
    
    return _actionType;
}

- (NSUInteger)cost {
    
    // Push action cost no actionpoints
    return 0;
}

+ (void)performPushFromAction:(Action*)action gameManager:(GameManager*)gamemanager withCompletion:(void (^)())completion {
    
    GridLocation *pushLocation = [action.enemyCard.cardLocation getPushLocationForGridLocationWhenComingFromGridLocation:[action getEntryLocationInPath]];
    
    Card *cardAtPushLocation = [gamemanager cardLocatedAtGridLocation:pushLocation];
    
    if (cardAtPushLocation != nil || ![pushLocation isInsideGameBoard]) {
        
        [gamemanager attackSuccessfulAgainstCard:action.enemyCard];
        completion();
    }
    else {
        PushAction *pushAction = [[PushAction alloc] initWithGameManager:gamemanager path:@[[[PathFinderStep alloc] initWithLocation:pushLocation]] andCardInAction:action.enemyCard];
        
        pushAction.delegate = action.delegate;
        [pushAction performActionWithCompletion:^{
            completion();
        }];
    }
}

- (void)performActionWithCompletion:(void (^)())completion {
    
    _battleReport = [BattleReport battleReportWithAction:self];
    
    [self.cardInAction willPerformAction:self];
    [self.delegate beforePerformAction:self];
    
    [self.delegate action:self wantsToMoveFollowingPath:self.path withCompletion:^(GridLocation *endLocation) {
                
        if (![self.cardInAction.cardLocation isEqual:endLocation]) {
            
            [self.gamemanager card:self.cardInAction movedToGridLocation:endLocation];
            
            [self.delegate action:self wantsToMoveCard:self.cardInAction fromLocation:_startLocation toLocation:endLocation];
        }
        
        if (completion != nil) {
            completion();
        }
    }];
}

@end
