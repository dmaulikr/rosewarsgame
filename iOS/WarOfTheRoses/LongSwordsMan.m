//
//  LongSwordsMan.m
//  WarOfTheRoses
//
//  Created by Heine Skov Kristensen on 3/10/13.
//
//

#import "LongSwordsMan.h"
#import "Action.h"
#import "GameManager.h"
#import "PathFinderStep.h"
#import "MeleeAttackAction.h"
#import "StandardBattleStrategy.h"

@implementation LongSwordsMan

-(id)init {
    self = [super init];
    
    if (self) {
        
        self.cardType = kCardTypeSpecialUnit;
        self.unitType = kInfantry;
        self.unitName = kLongSwordsMan;
        self.unitAttackType = kUnitAttackTypeMelee;
        
        self.attack = [[RangeAttribute alloc] initWithStartingRange:MakeAttributeRange(4, 6)];
        
        self.defence = [[RangeAttribute alloc] initWithStartingRange:MakeAttributeRange(1, 3)];
        
        self.range = 1;
        self.move = 1;
        self.moveActionCost = self.attackActionCost = 1;
        self.hitpoints = 1;
        
        self.attackSound = @"sword_sound.wav";
        self.defeatSound = @"infantry_defeated_sound.mp3";

        self.frontImageSmall = @"longswordsman_icon.png";
        self.frontImageLarge = [NSString stringWithFormat:@"longswordsman_%d.png", self.cardColor];
        
        [self commonInit];
    }
    
    return self;
}

+ (id)card {
    
    return [[LongSwordsMan alloc] init];
}

- (void)didPerformedAction:(Action *)action {
    
    [super didPerformedAction:action];
    
    MeleeAttackAction *meleeAttackAction = (MeleeAttackAction*)action;
    
    if (meleeAttackAction.isAttack) {
        
        // Get 4 nearby tiles in attackdirection
        GridLocation *startLocation = meleeAttackAction.startLocation;
        GridLocation *endLocation = [meleeAttackAction getLastLocationInPath];
        
        NSMutableSet *surroundingMyCard = [NSMutableSet setWithArray:[startLocation surroundingEightGridLocations]];
        NSSet *surroundingEnemyCard = [NSSet setWithArray:[endLocation surroundingEightGridLocations]];
        
        [surroundingMyCard intersectSet:surroundingEnemyCard];
        
        for (GridLocation *gridLocation in surroundingMyCard.allObjects) {
            
            Card *cardInLocation = [[GameManager sharedManager] cardLocatedAtGridLocation:gridLocation];
            
            if (cardInLocation != nil && cardInLocation.cardColor != meleeAttackAction.cardInAction.cardColor) {
                
                MeleeAttackAction *meleeAction = [[MeleeAttackAction alloc] initWithPath:@[[[PathFinderStep alloc] initWithLocation:gridLocation]] andCardInAction:action.cardInAction enemyCard:cardInLocation meleeAttackType:kMeleeAttackTypeNormal];
                
                BattleReport *battleReport = [BattleReport battleReportWithAction:meleeAction];
                id<BattleStrategy> battleStrategyForBattle = action.cardInAction.battleStrategy;
                
                if (action.playback) {
                    
                    BaseBattleStrategy *battleStrategy = [meleeAttackAction.secondaryActionsForPlayback objectForKey:gridLocation];
                    
                    if (battleStrategy != nil) {
                        battleStrategyForBattle = battleStrategy;
                    }
                }

                BattleResult *outcome = [[GameManager sharedManager] resolveCombatBetween:action.cardInAction defender:cardInLocation battleStrategy:battleStrategyForBattle];
                
                outcome.meleeAttackType = meleeAction.meleeAttackType;
                battleReport.primaryBattleResult = outcome;
                
                if (!action.playback) {
                    [action.battleReport.secondaryBattleReports addObject:battleReport];
                }
                
                [action.delegate action:meleeAction hasResolvedCombatWithOutcome:outcome.combatOutcome];
            }
        }
    }
}

@end
