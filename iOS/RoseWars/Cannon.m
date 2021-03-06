//
//  Canon.m
//  WarOfTheRoses
//
//  Created by Heine Skov Kristensen on 2/28/13.
//
//

#import "Cannon.h"
#import "Action.h"
#import "GameManager.h"

@implementation Cannon

@synthesize isQuarantined = _isQuarantined;

-(id)init {
    self = [super init];
    
    if (self) {
        
        self.cardType = kCardTypeSpecialUnit;
        self.unitType = kSpecialUnit;
        self.unitName = kCannon;
        self.unitAttackType = kUnitAttackTypeRanged;
        
        self.attack = [[HKAttribute alloc] initWithStartingValue:5];
        self.defence = [[HKAttribute alloc] initWithStartingValue:1];
        
        self.range = 4;
        self.move = 1;
        self.moveActionCost = self.attackActionCost = 1;
        self.hitpoints = 1;
        
        _lastAttackInRound = 0;
        
        self.attackSound = @"sword_sound.wav";
        self.defeatSound = @"defeat.mp3";
        
        self.frontImageSmall = @"cannon_icon.png";
        self.frontImageLarge = [NSString stringWithFormat:@"cannon_%d.png", self.cardColor];
        
        [self commonInit];
    }
    
    return self;
}

+ (id)card {
    return [[Cannon alloc] init];
}

- (void)didPerformedAction:(Action *)action {
    
    [super didPerformedAction:action];

    if (action.isAttack) {
        _isQuarantined = YES;
        _lastAttackInRound = self.gamemanager.currentGame.currentRound;
    }
}

- (BOOL)canPerformActionOfType:(ActionTypes)actionType withRemainingActionCount:(NSUInteger)remainingActionCount {
    
    BOOL canPerformAction = [super canPerformActionOfType:actionType withRemainingActionCount:remainingActionCount];
    
    if (actionType == kActionTypeRanged) {
        if (_isQuarantined && (self.gamemanager.currentGame.currentRound - _lastAttackInRound < 3)) {
            canPerformAction = NO;
        }
        else {
            _isQuarantined = NO;
        }
    }
    
    return canPerformAction;
}

- (NSDictionary *)asDictionary {
    
    return [NSDictionary dictionaryWithObjectsAndKeys:@(_isQuarantined), @"is_quarantined", @(_lastAttackInRound), @"last_attack_in_round", nil];
}

- (void)fromDictionary:(NSDictionary*)dictionary {
    
    _isQuarantined = [[dictionary valueForKey:@"is_quarantined"] boolValue];
    _lastAttackInRound = [[dictionary valueForKey:@"last_attack_in_round"] integerValue];
}

@end
